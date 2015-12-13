var path = require('path');
var supertest = require('supertest');

var app = require(path.join(__dirname, '../../app'));

describe('GET /:file', function () {
  'use strict';
  it('should return a 404 if the file does not exist', function (done) {
    supertest(app).get('/doesnotexist').expect(404).end(done);
  });
});

describe('PUT /:file', function () {
  'use strict';
  it('should return a 200 if a file is sent', function (done) {
    supertest(app).put('/file').send(path.join(__dirname, '../../package.json')).expect(200).end(done);
  });

  it('should return a 400 if a file is not sent', function (done) {
    supertest(app).put('/file').expect(400).end(done);
  });
});