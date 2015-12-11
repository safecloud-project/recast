var express = require('express');
var fs = require('fs');
var path = require('path');
var rawBody = require('raw-body');
var router = express.Router();
var typer = require('media-typer');

function RS(messageLength, errorCorrectionLength) {
  'use strict';
	var dataLength = messageLength - errorCorrectionLength;
	var encoder = new rs.ReedSolomonEncoder(rs.GenericGF.AZTEC_DATA_8());
	var decoder = new rs.ReedSolomonDecoder(rs.GenericGF.AZTEC_DATA_8());
	return {
		dataLength: dataLength,
		messageLength: messageLength,
		errorCorrectionLength: errorCorrectionLength,

		encode : function (message) {
			encoder.encode(message, errorCorrectionLength);
		},

		decode: function (message) {
			decoder.decode(message, errorCorrectionLength);
		}
	};
}

router.get('/(:path)', function(req, res, next) {
  'use strict';
  var resourcePath = path.join(__dirname, '../data/' , path.normalize(req.path));
  var stream = fs.createReadStream(resourcePath, {
    'autoclose': true,
    'flags': 'r'
  });
  if (!stream) {
    return res.status(500).send('NOK');
  }
  res.status(200);
  stream.pipe(res);
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
  //TODO: Handle file path with folder arborescence with 'mkdirp'
  var fileLocation = path.join(__dirname, '../data/' , req.path);
  fs.writeFile(fileLocation, req.data, function (error) {
    if (error) {
      return res.status(error.status || 500).send('NOK');
    }
    res.status(200).send('OK');
  });
});

module.exports = router;
