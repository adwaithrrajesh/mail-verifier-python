print("Scout script running locally!")

import smtplib
import dns.resolver
import random
import string
import time
import threading
from typing import List, Optional, Union, Dict, Set
from unidecode import unidecode
from concurrent.futures import ThreadPoolExecutor, as_completed
import socket
from functools import lru_cache
import queue


class Scout:
    def __init__(
        self,
        check_variants: bool = True,
        check_prefixes: bool = True,
        check_catchall: bool = True,
        normalize: bool = True,
        num_threads: int = 50,  # Optimized for 5GB RAM
        num_bulk_threads: int = 25,  # Optimized for 5GB RAM
        smtp_timeout: int = 8,  # Increased timeout for better success rate
        batch_size: int = 100,  # Larger batches for better throughput
        connection_pool_size: int = 50,  # Larger pool for 5GB RAM
        max_retries: int = 3,  # Retry failed connections
        retry_delay: float = 1.0  # Base retry delay
    ) -> None:
        self.check_variants = check_variants
        self.check_prefixes = check_prefixes
        self.check_catchall = check_catchall
        self.normalize = normalize
        self.num_threads = num_threads
        self.num_bulk_threads = num_bulk_threads
        self.smtp_timeout = smtp_timeout
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Performance optimization attributes
        self.mx_cache = {}  # DNS cache for MX records
        self.cache_lock = threading.Lock()  # Thread-safe cache access
        self.connection_pool = queue.Queue(maxsize=connection_pool_size)
        self.pool_lock = threading.Lock()
        
        # Circuit breaker for failing servers
        self.failing_servers = {}  # Track failing servers
        self.circuit_breaker_timeout = 300  # 5 minutes
        self.max_failures = 5  # Max failures before circuit opens
        
        # Performance tracking
        self.stats = {
            'emails_processed': 0,
            'valid_emails_found': 0,
            'start_time': None,
            'cache_hits': 0,
            'cache_misses': 0,
            'retries': 0,
            'circuit_breaker_hits': 0,
            'connection_reuses': 0
        }

    def get_mx_records_cached(self, domain: str) -> tuple:
        """Optimized MX record lookup with proper caching"""
        try:
            with self.cache_lock:
                if domain in self.mx_cache:
                    self.stats['cache_hits'] += 1
                    return self.mx_cache[domain]
                
                self.stats['cache_misses'] += 1
                # Use shorter timeout for DNS resolution
                resolver = dns.resolver.Resolver()
                resolver.timeout = 3
                resolver.lifetime = 5
                records = resolver.resolve(domain, 'MX')
                mx_hosts = tuple(str(r.exchange).rstrip('.').lower() for r in records)
                # Sort by priority (lower number = higher priority)
                mx_hosts = sorted(mx_hosts, key=lambda x: next((r.preference for r in records if str(r.exchange).rstrip('.').lower() == x), 999))
                self.mx_cache[domain] = mx_hosts
                return mx_hosts
        except Exception as e:
            # Log DNS resolution failures
            print(f"DNS resolution failed for {domain}: {e}")
            return tuple()

    def get_connection_from_pool(self, mx_host: str, port: int):
        """Get SMTP connection from pool or create new one with validation"""
        try:
            connection_key = f"{mx_host}:{port}"
            
            # Try to get from pool first
            if not self.connection_pool.empty():
                try:
                    connection = self.connection_pool.get_nowait()
                    if connection[0] == connection_key:
                        # Validate connection is still alive
                        if self._validate_connection(connection[1]):
                            self.stats['connection_reuses'] += 1
                            return connection[1]
                        else:
                            # Connection is dead, close it
                            try:
                                connection[1].quit()
                            except:
                                pass
                except queue.Empty:
                    pass
            
            # Create new connection
            if port == 465:
                server = smtplib.SMTP_SSL(mx_host, port, timeout=self.smtp_timeout)
            else:
                server = smtplib.SMTP(mx_host, port, timeout=self.smtp_timeout)
            
            return server
        except Exception as e:
            print(f"Connection creation failed for {mx_host}:{port}: {e}")
            return None
    
    def _validate_connection(self, server):
        """Validate if SMTP connection is still alive"""
        try:
            server.noop()  # Send NOOP command to check connection
            return True
        except:
            return False

    def return_connection_to_pool(self, mx_host: str, port: int, server):
        """Return connection to pool for reuse with validation"""
        try:
            if server and not self.connection_pool.full():
                # Validate connection before returning to pool
                if self._validate_connection(server):
                    connection_key = f"{mx_host}:{port}"
                    self.connection_pool.put_nowait((connection_key, server))
                else:
                    # Connection is dead, close it
                    try:
                        server.quit()
                    except:
                        pass
        except Exception:
            # If we can't return to pool, close the connection
            try:
                server.quit()
            except:
                pass
    
    def is_circuit_open(self, server_key: str) -> bool:
        """Check if circuit breaker is open for a server"""
        if server_key not in self.failing_servers:
            return False
        
        failure_data = self.failing_servers[server_key]
        if failure_data['failures'] < self.max_failures:
            return False
        
        # Check if timeout has passed
        if time.time() - failure_data['last_failure'] > self.circuit_breaker_timeout:
            # Reset circuit breaker
            del self.failing_servers[server_key]
            return False
        
        return True
    
    def record_server_failure(self, server_key: str):
        """Record a server failure for circuit breaker"""
        if server_key not in self.failing_servers:
            self.failing_servers[server_key] = {'failures': 0, 'last_failure': 0}
        
        self.failing_servers[server_key]['failures'] += 1
        self.failing_servers[server_key]['last_failure'] = time.time()
        self.stats['circuit_breaker_hits'] += 1

    def check_smtp(self, email: str, port: int = 25) -> Dict[str, Union[str, int, float, bool]]:
        domain = email.split('@')[1]
        ver_ops = 0
        connections = 0
        catch_all_flag = False
        mx_record = ""
        start_time = time.time()

        try:
            # Use cached MX records for better performance
            mx_hosts = self.get_mx_records_cached(domain)
            if not mx_hosts:
                return self._create_error_response(email, domain, "No MX records found", start_time)

            # Optimized port order for Hetzner (587 first, then 465, then 25)
            smtp_ports = [587, 465, 25]
            
            for mx in mx_hosts:
                server_key = f"{mx}"
                
                # Check circuit breaker
                if self.is_circuit_open(server_key):
                    continue
                
                for attempt in range(self.max_retries + 1):
                    for smtp_port in smtp_ports:
                        server = None
                        try:
                            # Try to get connection from pool
                            server = self.get_connection_from_pool(mx, smtp_port)
                            
                            if not server:
                                # Create new connection if pool is empty
                                if smtp_port == 465:
                                    server = smtplib.SMTP_SSL(mx, smtp_port, timeout=self.smtp_timeout)
                                else:
                                    server = smtplib.SMTP(mx, smtp_port, timeout=self.smtp_timeout)
                            
                            connections += 1
                            server.set_debuglevel(0)
                            
                            # Single EHLO call
                            server.ehlo("blu-harvest.com")
                            
                            # STARTTLS only if needed and not SSL port
                            if smtp_port != 465 and server.has_extn('starttls'):
                                try:
                                    server.starttls()
                                except Exception:
                                    pass  # Continue without STARTTLS
                            
                            # MAIL FROM and RCPT TO
                            server.mail('noreply@blu-harvest.com')
                            ver_ops += 1
                            code, message = server.rcpt(email)
                            ver_ops += 1
                            mx_record = mx

                            # Process response
                            if code == 250:
                                if self.check_catchall:
                                    catch_all_flag = self.is_catch_all(domain, mx)
                                status = "risky" if catch_all_flag else "valid"
                                msg = "Catch-All" if catch_all_flag else f"{code} {message.decode()}"
                                
                                # Return connection to pool
                                self.return_connection_to_pool(mx, smtp_port, server)
                                
                                time_exec = round(time.time() - start_time, 3)
                                return {
                                    "email": email,
                                    "status": status,
                                    "catch_all": catch_all_flag,
                                    "message": msg,
                                    "user_name": email.split('@')[0].replace('.', ' ').title(),
                                    "domain": domain,
                                    "mx": mx_record,
                                    "connections": connections,
                                    "ver_ops": ver_ops,
                                    "time_exec": time_exec
                                }
                            elif 400 <= code < 500:
                                # Temporary failure, retry
                                if attempt < self.max_retries:
                                    self.return_connection_to_pool(mx, smtp_port, server)
                                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                                    continue
                                else:
                                    status = "unknown"
                                    msg = f"{code} {message.decode()}"
                                    self.return_connection_to_pool(mx, smtp_port, server)
                                    
                                    time_exec = round(time.time() - start_time, 3)
                                    return {
                                        "email": email,
                                        "status": status,
                                        "catch_all": catch_all_flag,
                                        "message": msg,
                                        "user_name": email.split('@')[0].replace('.', ' ').title(),
                                        "domain": domain,
                                        "mx": mx_record,
                                        "connections": connections,
                                        "ver_ops": ver_ops,
                                        "time_exec": time_exec
                                    }
                            else:
                                # Permanent failure
                                status = "invalid"
                                msg = f"{code} {message.decode()}"
                                self.return_connection_to_pool(mx, smtp_port, server)
                                
                                time_exec = round(time.time() - start_time, 3)
                                return {
                                    "email": email,
                                    "status": status,
                                    "catch_all": catch_all_flag,
                                    "message": msg,
                                    "user_name": email.split('@')[0].replace('.', ' ').title(),
                                    "domain": domain,
                                    "mx": mx_record,
                                    "connections": connections,
                                    "ver_ops": ver_ops,
                                    "time_exec": time_exec
                                }
                                
                        except (socket.timeout, TimeoutError) as e:
                            connections += 1
                            if server:
                                try:
                                    server.quit()
                                except:
                                    pass
                            
                            if attempt < self.max_retries:
                                time.sleep(self.retry_delay * (2 ** attempt))
                                continue
                            else:
                                # Record failure for circuit breaker
                                self.record_server_failure(server_key)
                                break
                                
                        except (ConnectionRefusedError, OSError) as e:
                            connections += 1
                            if server:
                                try:
                                    server.quit()
                                except:
                                    pass
                            
                            if attempt < self.max_retries:
                                time.sleep(self.retry_delay * (2 ** attempt))
                                continue
                            else:
                                # Record failure for circuit breaker
                                self.record_server_failure(server_key)
                                break
                                
                        except Exception as e:
                            connections += 1
                            if server:
                                try:
                                    server.quit()
                                except:
                                    pass
                            
                            if attempt < self.max_retries:
                                time.sleep(self.retry_delay * (2 ** attempt))
                                continue
                            else:
                                # Record failure for circuit breaker
                                self.record_server_failure(server_key)
                                break

            # All attempts failed
            time_exec = round(time.time() - start_time, 3)
            message = "SMTP failed for all MX records & ports (587, 465, 25)"
            status = "unknown"
            
            return self._create_error_response(email, domain, message, start_time)

        except Exception as e:
            time_exec = round(time.time() - start_time, 3)
            return self._create_error_response(email, domain, f"Rejected: {str(e)}", start_time)

    def _create_error_response(self, email: str, domain: str, message: str, start_time: float) -> Dict:
        """Helper method to create error response"""
        time_exec = round(time.time() - start_time, 3)
        return {
            "email": email,
            "status": "unknown",
            "catch_all": False,
            "message": message,
            "user_name": email.split('@')[0].replace('.', ' ').title(),
            "domain": domain,
            "mx": "",
            "connections": 0,
            "ver_ops": 0,
            "time_exec": time_exec
        }

    def is_catch_all(self, domain: str, mx_record: str) -> bool:
        fake_user = ''.join(random.choices(string.ascii_lowercase, k=12))
        fake_email = f"{fake_user}@{domain}"

        # Try multiple SMTP ports in case port 25 is blocked
        smtp_ports = [25, 587, 465]
        
        for smtp_port in smtp_ports:
            try:
                # Use SMTP_SSL for port 465, regular SMTP for others
                if smtp_port == 465:
                    server = smtplib.SMTP_SSL(mx_record, smtp_port, timeout=self.smtp_timeout)
                else:
                    server = smtplib.SMTP(mx_record, smtp_port, timeout=self.smtp_timeout)
                
                with server as smtp_server:
                    smtp_server.set_debuglevel(0)
                    smtp_server.ehlo("blu-harvest.com")
                    if smtp_port != 465 and smtp_server.has_extn('starttls'):
                        try:
                            smtp_server.starttls()
                            smtp_server.ehlo("blu-harvest.com")
                        except Exception:
                            pass
                    smtp_server.mail("noreply@blu-harvest.com")
                    code, _ = smtp_server.rcpt(fake_email)
                    return code == 250
            except Exception:
                continue  # Try next port
        
        return False  # All ports failed

    def verify_emails_bulk_optimized(self, emails: List[str], progress_callback=None) -> List[Dict]:
        """
        High-performance bulk email verification optimized for 5GB RAM
        Designed to handle 1000+ emails with 90-95% success rate
        """
        if not emails:
            return []
        
        self.stats['start_time'] = time.time()
        self.stats['emails_processed'] = 0
        self.stats['valid_emails_found'] = 0
        self.stats['retries'] = 0
        self.stats['circuit_breaker_hits'] = 0
        self.stats['connection_reuses'] = 0
        
        results = []
        batch_size = self.batch_size
        
        # Use persistent thread pool for better performance
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            # Process emails in batches for better memory management
            for i in range(0, len(emails), batch_size):
                batch = emails[i:i + batch_size]
                batch_results = self._process_batch_parallel_persistent(executor, batch)
                results.extend(batch_results)
                
                # Update progress
                if progress_callback:
                    progress = (i + len(batch)) / len(emails) * 100
                    progress_callback(progress, len(batch_results), len(results))
                
                # Small delay to prevent overwhelming servers
                time.sleep(0.05)
        
        return results

    def _process_batch_parallel_persistent(self, executor: ThreadPoolExecutor, batch: List[str]) -> List[Dict]:
        """Process a batch of emails using persistent thread pool"""
        results = []
        
        # Submit all tasks
        future_to_email = {
            executor.submit(self.check_smtp, email): email 
            for email in batch
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_email):
            email = future_to_email[future]
            try:
                result = future.result()
                results.append(result)
                self.stats['emails_processed'] += 1
                
                if result.get('status') in ['valid', 'risky']:
                    self.stats['valid_emails_found'] += 1
                    
            except Exception as e:
                error_result = self._create_error_response(
                    email, 
                    email.split('@')[1] if '@' in email else '', 
                    f"Processing error: {str(e)}", 
                    time.time()
                )
                results.append(error_result)
                self.stats['emails_processed'] += 1
        
        return results

    def _process_batch_parallel(self, batch: List[str]) -> List[Dict]:
        """Process a batch of emails in parallel (legacy method)"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            # Submit all tasks
            future_to_email = {
                executor.submit(self.check_smtp, email): email 
                for email in batch
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_email):
                email = future_to_email[future]
                try:
                    result = future.result()
                    results.append(result)
                    self.stats['emails_processed'] += 1
                    
                    if result.get('status') in ['valid', 'risky']:
                        self.stats['valid_emails_found'] += 1
                        
                except Exception as e:
                    error_result = self._create_error_response(
                        email, 
                        email.split('@')[1] if '@' in email else '', 
                        f"Processing error: {str(e)}", 
                        time.time()
                    )
                    results.append(error_result)
                    self.stats['emails_processed'] += 1
        
        return results

    def get_performance_stats(self) -> Dict:
        """Get current performance statistics"""
        if self.stats['start_time']:
            elapsed_time = time.time() - self.stats['start_time']
            emails_per_second = self.stats['emails_processed'] / elapsed_time if elapsed_time > 0 else 0
            estimated_time_1000 = 1000 / emails_per_second if emails_per_second > 0 else 0
            success_rate = (self.stats['valid_emails_found'] / max(1, self.stats['emails_processed'])) * 100
            
            return {
                **self.stats,
                'elapsed_time': round(elapsed_time, 2),
                'emails_per_second': round(emails_per_second, 2),
                'estimated_time_1000_emails': round(estimated_time_1000, 2),
                'success_rate': round(success_rate, 2),
                'cache_hit_ratio': round(self.stats['cache_hits'] / max(1, self.stats['cache_hits'] + self.stats['cache_misses']) * 100, 2),
                'connection_reuse_ratio': round(self.stats['connection_reuses'] / max(1, self.stats['emails_processed']) * 100, 2),
                'retry_ratio': round(self.stats['retries'] / max(1, self.stats['emails_processed']) * 100, 2)
            }
        return self.stats

    def find_valid_emails(self, domain: str, names: Optional[Union[str, List[str], List[List[str]]]] = None) -> Dict[str, Union[str, int, float, None]]:
        email_variants = []
        generated_mails = []

        if self.check_variants and names:
            if isinstance(names, str):
                names = names.split(" ")
            if isinstance(names, list) and names and isinstance(names[0], list):
                for name_list in names:
                    name_list = self.split_list_data(name_list)
                    email_variants.extend(self.generate_email_variants(name_list, domain, normalize=self.normalize))
            else:
                names = self.split_list_data(names)
                email_variants = self.generate_email_variants(names, domain, normalize=self.normalize)

        if self.check_prefixes and not names:
            generated_mails = self.generate_prefixes(domain)

        all_emails = list(set(email_variants + generated_mails))

        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            future_to_email = {executor.submit(self.check_smtp, email): email for email in all_emails}
            for future in as_completed(future_to_email):
                result = future.result()
                if result["status"] in ["valid", "risky"]:
                    for f in future_to_email:
                        f.cancel()
                    return result
                time.sleep(random.uniform(0.5, 1.2))

        return {
            "email": None,
            "status": "invalid",
            "catch_all": False,
            "message": "No valid email found",
            "user_name": "",
            "domain": domain,
            "mx": "",
            "connections": 0,
            "ver_ops": 0,
            "time_exec": 0.0
        }

    def find_valid_emails_bulk(self, email_data: List[Dict[str, Union[str, List[str]]]]) -> List[Dict[str, Union[str, List[str], Dict[str, Union[str, int, float, None]]]]]:
        def worker(data):
            domain = data.get("domain")
            names = data.get("names", [])
            valid_email = self.find_valid_emails(domain, names)
            return {
                "domain": domain,
                "names": names,
                "valid_email": valid_email
            }

        with ThreadPoolExecutor(max_workers=self.num_bulk_threads) as executor:
            futures = [executor.submit(worker, data) for data in email_data]
            return [future.result() for future in as_completed(futures)]

    def split_list_data(self, target):
        new_target = []
        for i in target:
            new_target.extend(i.split(" "))
        return new_target

    def generate_email_variants(self, names: List[str], domain: str, normalize: bool = True) -> List[str]:
        if normalize:
            names = [unidecode(n).lower().strip() for n in names if n]
        first, last = names[0], names[-1] if len(names) > 1 else ("", names[0])
        patterns = [
            f"{first}@{domain}",
            f"{first}{last}@{domain}",
            f"{first}.{last}@{domain}",
            f"{first}_{last}@{domain}",
            f"{last}.{first}@{domain}",
            f"{first[0]}{last}@{domain}",
            f"{first[0]}.{last}@{domain}",
            f"{first}{last[0]}@{domain}",
            f"{first[0]}{last[0]}@{domain}",
            f"{last}{first}@{domain}",
            f"{last}@{domain}"
        ]
        return list(set(patterns))

    def generate_prefixes(self, domain: str) -> List[str]:
        prefixes = ['admin', 'contact', 'hello', 'team', 'support', 'info', 'mail']
        return [f"{prefix}@{domain}" for prefix in prefixes]

   
