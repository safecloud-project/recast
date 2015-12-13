var express = require('express');
var rawBody = require('raw-body');
var redis = require('redis');
var router = express.Router();
var typer = require('media-typer');

router.get('/(:path)', function(req, res) {
  'use strict';
  var redisClient = redis.createClient({'return_buffers': true});
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
    req.data = string;
    next();
  });
}

router.put('/(:path)', rawBodyUpload, function (req, res) {
  'use strict';
  var redisClient = redis.createClient();
  redisClient.set(req.path, req.data, function (error) {
    if (error) {
      return res.status(error.status || 500).send(error.message);
    }
    redisClient.end();
    res.status(200).send('OK');
  });
});

module.exports = router;
