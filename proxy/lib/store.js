module.exports = function () {
  var redis = require('redis');
  'use strict';
  var redisClient = redis.createClient({
    'host': process.env.REDIS_PORT_6379_TCP_ADDR || '127.0.0.1',
    'port':  process.env.REDIS_PORT_6379_TCP_PORT || 6379,
    'return_buffers': true
  });

  return {
    'delete': function (key, callback) {
      redisClient.del(key, callback);
    },
    'get': function (key, callback) {
      redisClient.get(key, callback);
    },
    'put': function (key, value, callback) {
      redisClient.set(key, value, callback);
    }
  };
};
