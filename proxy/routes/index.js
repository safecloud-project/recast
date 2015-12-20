var express = require('express');
var path = require('path');
var rawBody = require('raw-body');
var router = express.Router();
var typer = require('media-typer');

var store = require(path.join(__dirname, '../lib/store'))();


router.get('/(:path)', function(req, res) {
  'use strict';
  store.get(req.path, function (error, data) {
    if (error) {
      return res.status(error.status || 500).send(error.message);
    }
    if (!data) {
      return res.status(404).send('not found');
    }
    return res.status(200).send(data);
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
  store.put(req.path, req.data, function (error) {
    if (error) {
      return res.status(error.status || 500).send(error.message);
    }
    return res.status(200).send('OK');
  });
});

router.delete('/(:path)', function (req, res) {
  'use strict';
  store.delete(req.path, function (error) {
    if (error) {
      return res.status(error.status || 500).send(error.message);
    }
    return res.status(200).send('OK');
  });
});

module.exports = router;
