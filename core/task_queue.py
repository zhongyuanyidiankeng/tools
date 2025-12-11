"""
任务队列模块
基于 asyncio.Semaphore 实现并发控制
"""
import asyncio
from typing import Callable, Any, TypeVar
from functools import wraps

T = TypeVar('T')

# 最大并发处理数
MAX_CONCURRENT_TASKS = 3


class TaskQueue:
    """
    简单的内存任务队列，限制并发处理数
    用于控制文件处理等资源密集型操作的并发量
    """
    
    def __init__(self, max_concurrent: int = MAX_CONCURRENT_TASKS):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self._active_tasks = 0
        self._queued_tasks = 0
    
    @property
    def active_count(self) -> int:
        """当前正在执行的任务数"""
        return self._active_tasks
    
    @property
    def queued_count(self) -> int:
        """当前排队等待的任务数"""
        return self._queued_tasks
    
    @property
    def is_full(self) -> bool:
        """队列是否已满"""
        return self._active_tasks >= self.max_concurrent
    
    async def submit(self, task: Callable[[], Any]) -> Any:
        """
        提交任务执行
        超过并发限制时排队等待
        """
        self._queued_tasks += 1
        try:
            async with self.semaphore:
                self._queued_tasks -= 1
                self._active_tasks += 1
                try:
                    if asyncio.iscoroutinefunction(task):
                        return await task()
                    else:
                        return task()
                finally:
                    self._active_tasks -= 1
        except Exception:
            self._queued_tasks -= 1
            raise
    
    async def submit_async(self, coro) -> Any:
        """
        提交协程执行
        """
        self._queued_tasks += 1
        try:
            async with self.semaphore:
                self._queued_tasks -= 1
                self._active_tasks += 1
                try:
                    return await coro
                finally:
                    self._active_tasks -= 1
        except Exception:
            self._queued_tasks -= 1
            raise


def rate_limited(queue: TaskQueue):
    """
    装饰器：将函数包装为受队列限制的任务
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async def task():
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                return func(*args, **kwargs)
            return await queue.submit(task)
        return wrapper
    return decorator


# 全局任务队列实例
task_queue = TaskQueue(MAX_CONCURRENT_TASKS)
