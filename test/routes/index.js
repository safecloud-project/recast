var assert = require('assert');
var path = require('path');
var redis = require('redis');
var sinon = require('sinon');
var supertest = require('supertest');

var app = require(path.join(__dirname, '../../app'));

describe('GET /:file', function () {
  'use strict';
  
  before(function () {
    sinon.stub(redis.RedisClient.prototype, 'get', function (key, callback) {
      callback(null, null);
    });
  });
  
  after(function () {
    if (typeof redis.RedisClient.prototype.get.restore === 'function') {
      redis.RedisClient.prototype.get.restore();
    }
  });

  it('should return a 404 if the file does not exist', function (done) {
    var initialCallCount = redis.RedisClient.prototype.get.callCount;
    supertest(app).get('/doesnotexist').expect(404).expect(function () {
      assert.strictEqual(redis.RedisClient.prototype.get.callCount, initialCallCount + 1);
    }).end(done);
  });
});

describe('PUT /:file', function () {
  'use strict';
  
  before(function () {
    sinon.stub(redis.RedisClient.prototype, 'set', function (key, data, callback) {
      callback(null);
    });
  });


  after(function () {
    if (typeof redis.RedisClient.prototype.set.restore === 'function') {
      redis.RedisClient.prototype.set.restore();
    }
  });
  
  it('should return a 200 if a file is sent', function (done) {
    var initialCallCount = redis.RedisClient.prototype.set.callCount;
    supertest(app).put('/file').send(path.join(__dirname, '../../package.json')).expect(200).expect(function () {
      assert.strictEqual(redis.RedisClient.prototype.set.callCount, initialCallCount + 1);
    }).end(done);
  });

  it('should return a 400 if a file is not sent', function (done) {
    var initialCallCount = redis.RedisClient.prototype.set.callCount;
    supertest(app).put('/file').expect(400).expect(function () {
      assert.strictEqual(redis.RedisClient.prototype.set.callCount, initialCallCount);
    }).end(done);
  });
});

describe('DELETE /:file', function () {
  'use strict';

  before(function () {
    sinon.stub(redis.RedisClient.prototype, 'del', function (key, callback) {
      callback(null, 1);
    });
  });

  after(function () {
    if (typeof redis.RedisClient.prototype.del.restore === 'function') {
      redis.RedisClient.prototype.del.restore();
    }
  });

  it('should return a 200 if the file does not exist', function (done) {
    supertest(app).delete('/file').expect(200).end(done);
  });

  it('should try to delete the file', function (done) {
    var initialCallCount = redis.RedisClient.prototype.del.callCount;
    supertest(app).delete('/file').expect(200).expect(function () {
      assert.strictEqual(redis.RedisClient.prototype.del.callCount, initialCallCount + 1);
    }).end(done);
  });
});
