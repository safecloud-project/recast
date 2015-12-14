var express = require('express');
var rawBody = require('raw-body');
var redis = require('redis');
var router = express.Router();
var typer = require('media-typer');

var REDIS_OPTIONS = Object.freeze({
  'host': process.env.REDIS_PORT_6379_TCP_ADDR || '127.0.0.1',
  'port':  process.env.REDIS_PORT_6379_TCP_PORT || 6379,
  'return_buffers': true
});

router.get('/(:path)', function(req, res) {
  'use strict';
  var redisClient = redis.createClient(REDIS_OPTIONS);
  redisClient.get(req.path, function (error, data) {
    redisClient.end();
    if (error) {
      return res.status(error.status || 500).send(error.message);
    }
    if (!data) {
      return res.status(404).send('not found');
    }
    res.status(200).send(data);
  });
});

function rawBodyUpload(req, res, next) {
  'use strict';
  rawBody(req, {
    length: req.headers['content-length'],
    limit: '10gb',
    encoding: typer.parse(req.headers['content-type'] || 'application/octet-stream').parameters.charset
  }, function (err, string) {
    if (err) {
      return next(err);
    }
    if (!Buffer.isBuffer(string) || string.length === 0) {
      return res.status(400).send('file missing');
    }
    req.data = string;
    next();
  });
}

router.put('/(:path)', rawBodyUpload, function (req, res) {
  'use strict';
  var redisClient = redis.createClient(REDIS_OPTIONS);
  redisClient.set(req.path, req.data, function (error) {
    if (error) {
      return res.status(error.status || 500).send(error.message);
    }
    redisClient.end();
    res.status(200).send('OK');
  });
});

router.delete('/(:path)', function (req, res) {
  'use strict';
  var redisClient = redis.createClient(REDIS_OPTIONS);
  redisClient.del(req.path, function (error) {
    redisClient.end();
    if (error) {
      return res.status(error.status || 500).send(error.message);
    }
    return res.status(200).send('OK');
  });
});

module.exports = router;
