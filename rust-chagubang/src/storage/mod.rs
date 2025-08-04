// 📾 存储模块模块

pub mod redis;

// 再嬼出公共类型和函数
pub use redis::RedisStorage;
