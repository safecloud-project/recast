var express = require('express');
var fs = require('fs');
var path = require('path');
var logger = require('morgan');

var routes = require('./routes/index');

var app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');

// logging
var logFileOptions = {
  'flags': 'a', //Work in append mode
  'encoding': 'utf8',
  'mode': 0666
};
var accessLogStream = fs.createWriteStream(path.join(__dirname, '/access.log'), logFileOptions);
var logOptions = {
  'stream': accessLogStream
};
app.use(logger('combined', logOptions));

app.use(express.static(path.join(__dirname, 'public')));

app.use('/', routes);

app.use('*', function (req, res) {
  'use strict';
  res.status(404).send('No route defined for ' + req.path);
});

module.exports = app;
