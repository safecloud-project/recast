var express = require('express');
var path = require('path');
var logger = require('morgan');

var routes = require('./routes/index');

var app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');

app.use(logger('dev'));

app.use(express.static(path.join(__dirname, 'public')));

app.use('/', routes);

app.use('*', function (req, res) {
  'use strict';
  res.status(404).send('No route defined for ' + req.path);
});

module.exports = app;