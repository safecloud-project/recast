package ch.unine.iiun.safecloud;

import static io.grpc.stub.ClientCalls.asyncUnaryCall;
import static io.grpc.stub.ClientCalls.asyncServerStreamingCall;
import static io.grpc.stub.ClientCalls.asyncClientStreamingCall;
import static io.grpc.stub.ClientCalls.asyncBidiStreamingCall;
import static io.grpc.stub.ClientCalls.blockingUnaryCall;
import static io.grpc.stub.ClientCalls.blockingServerStreamingCall;
import static io.grpc.stub.ClientCalls.futureUnaryCall;
import static io.grpc.MethodDescriptor.generateFullMethodName;
import static io.grpc.stub.ServerCalls.asyncUnaryCall;
import static io.grpc.stub.ServerCalls.asyncServerStreamingCall;
import static io.grpc.stub.ServerCalls.asyncClientStreamingCall;
import static io.grpc.stub.ServerCalls.asyncBidiStreamingCall;

@javax.annotation.Generated("by gRPC proto compiler")
public class EncoderDecoderGrpc {

  private EncoderDecoderGrpc() {}

  public static final String SERVICE_NAME = "EncoderDecoder";

  // Static method descriptors that strictly reflect the proto.
  @io.grpc.ExperimentalApi
  public static final io.grpc.MethodDescriptor<ch.unine.iiun.safecloud.Playcloud.EncodeRequest,
      ch.unine.iiun.safecloud.Playcloud.EncodeReply> METHOD_ENCODE =
      io.grpc.MethodDescriptor.create(
          io.grpc.MethodDescriptor.MethodType.UNARY,
          generateFullMethodName(
              "EncoderDecoder", "Encode"),
          io.grpc.protobuf.ProtoUtils.marshaller(ch.unine.iiun.safecloud.Playcloud.EncodeRequest.getDefaultInstance()),
          io.grpc.protobuf.ProtoUtils.marshaller(ch.unine.iiun.safecloud.Playcloud.EncodeReply.getDefaultInstance()));
  @io.grpc.ExperimentalApi
  public static final io.grpc.MethodDescriptor<ch.unine.iiun.safecloud.Playcloud.DecodeRequest,
      ch.unine.iiun.safecloud.Playcloud.DecodeReply> METHOD_DECODE =
      io.grpc.MethodDescriptor.create(
          io.grpc.MethodDescriptor.MethodType.UNARY,
          generateFullMethodName(
              "EncoderDecoder", "Decode"),
          io.grpc.protobuf.ProtoUtils.marshaller(ch.unine.iiun.safecloud.Playcloud.DecodeRequest.getDefaultInstance()),
          io.grpc.protobuf.ProtoUtils.marshaller(ch.unine.iiun.safecloud.Playcloud.DecodeReply.getDefaultInstance()));

  public static EncoderDecoderStub newStub(io.grpc.Channel channel) {
    return new EncoderDecoderStub(channel);
  }

  public static EncoderDecoderBlockingStub newBlockingStub(
      io.grpc.Channel channel) {
    return new EncoderDecoderBlockingStub(channel);
  }

  public static EncoderDecoderFutureStub newFutureStub(
      io.grpc.Channel channel) {
    return new EncoderDecoderFutureStub(channel);
  }

  public static interface EncoderDecoder {

    public void encode(ch.unine.iiun.safecloud.Playcloud.EncodeRequest request,
        io.grpc.stub.StreamObserver<ch.unine.iiun.safecloud.Playcloud.EncodeReply> responseObserver);

    public void decode(ch.unine.iiun.safecloud.Playcloud.DecodeRequest request,
        io.grpc.stub.StreamObserver<ch.unine.iiun.safecloud.Playcloud.DecodeReply> responseObserver);
  }

  public static interface EncoderDecoderBlockingClient {

    public ch.unine.iiun.safecloud.Playcloud.EncodeReply encode(ch.unine.iiun.safecloud.Playcloud.EncodeRequest request);

    public ch.unine.iiun.safecloud.Playcloud.DecodeReply decode(ch.unine.iiun.safecloud.Playcloud.DecodeRequest request);
  }

  public static interface EncoderDecoderFutureClient {

    public com.google.common.util.concurrent.ListenableFuture<ch.unine.iiun.safecloud.Playcloud.EncodeReply> encode(
        ch.unine.iiun.safecloud.Playcloud.EncodeRequest request);

    public com.google.common.util.concurrent.ListenableFuture<ch.unine.iiun.safecloud.Playcloud.DecodeReply> decode(
        ch.unine.iiun.safecloud.Playcloud.DecodeRequest request);
  }

  public static class EncoderDecoderStub extends io.grpc.stub.AbstractStub<EncoderDecoderStub>
      implements EncoderDecoder {
    private EncoderDecoderStub(io.grpc.Channel channel) {
      super(channel);
    }

    private EncoderDecoderStub(io.grpc.Channel channel,
        io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected EncoderDecoderStub build(io.grpc.Channel channel,
        io.grpc.CallOptions callOptions) {
      return new EncoderDecoderStub(channel, callOptions);
    }

    @java.lang.Override
    public void encode(ch.unine.iiun.safecloud.Playcloud.EncodeRequest request,
        io.grpc.stub.StreamObserver<ch.unine.iiun.safecloud.Playcloud.EncodeReply> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(METHOD_ENCODE, getCallOptions()), request, responseObserver);
    }

    @java.lang.Override
    public void decode(ch.unine.iiun.safecloud.Playcloud.DecodeRequest request,
        io.grpc.stub.StreamObserver<ch.unine.iiun.safecloud.Playcloud.DecodeReply> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(METHOD_DECODE, getCallOptions()), request, responseObserver);
    }
  }

  public static class EncoderDecoderBlockingStub extends io.grpc.stub.AbstractStub<EncoderDecoderBlockingStub>
      implements EncoderDecoderBlockingClient {
    private EncoderDecoderBlockingStub(io.grpc.Channel channel) {
      super(channel);
    }

    private EncoderDecoderBlockingStub(io.grpc.Channel channel,
        io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected EncoderDecoderBlockingStub build(io.grpc.Channel channel,
        io.grpc.CallOptions callOptions) {
      return new EncoderDecoderBlockingStub(channel, callOptions);
    }

    @java.lang.Override
    public ch.unine.iiun.safecloud.Playcloud.EncodeReply encode(ch.unine.iiun.safecloud.Playcloud.EncodeRequest request) {
      return blockingUnaryCall(
          getChannel().newCall(METHOD_ENCODE, getCallOptions()), request);
    }

    @java.lang.Override
    public ch.unine.iiun.safecloud.Playcloud.DecodeReply decode(ch.unine.iiun.safecloud.Playcloud.DecodeRequest request) {
      return blockingUnaryCall(
          getChannel().newCall(METHOD_DECODE, getCallOptions()), request);
    }
  }

  public static class EncoderDecoderFutureStub extends io.grpc.stub.AbstractStub<EncoderDecoderFutureStub>
      implements EncoderDecoderFutureClient {
    private EncoderDecoderFutureStub(io.grpc.Channel channel) {
      super(channel);
    }

    private EncoderDecoderFutureStub(io.grpc.Channel channel,
        io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected EncoderDecoderFutureStub build(io.grpc.Channel channel,
        io.grpc.CallOptions callOptions) {
      return new EncoderDecoderFutureStub(channel, callOptions);
    }

    @java.lang.Override
    public com.google.common.util.concurrent.ListenableFuture<ch.unine.iiun.safecloud.Playcloud.EncodeReply> encode(
        ch.unine.iiun.safecloud.Playcloud.EncodeRequest request) {
      return futureUnaryCall(
          getChannel().newCall(METHOD_ENCODE, getCallOptions()), request);
    }

    @java.lang.Override
    public com.google.common.util.concurrent.ListenableFuture<ch.unine.iiun.safecloud.Playcloud.DecodeReply> decode(
        ch.unine.iiun.safecloud.Playcloud.DecodeRequest request) {
      return futureUnaryCall(
          getChannel().newCall(METHOD_DECODE, getCallOptions()), request);
    }
  }

  public static io.grpc.ServerServiceDefinition bindService(
      final EncoderDecoder serviceImpl) {
    return io.grpc.ServerServiceDefinition.builder(SERVICE_NAME)
      .addMethod(
        METHOD_ENCODE,
        asyncUnaryCall(
          new io.grpc.stub.ServerCalls.UnaryMethod<
              ch.unine.iiun.safecloud.Playcloud.EncodeRequest,
              ch.unine.iiun.safecloud.Playcloud.EncodeReply>() {
            @java.lang.Override
            public void invoke(
                ch.unine.iiun.safecloud.Playcloud.EncodeRequest request,
                io.grpc.stub.StreamObserver<ch.unine.iiun.safecloud.Playcloud.EncodeReply> responseObserver) {
              serviceImpl.encode(request, responseObserver);
            }
          }))
      .addMethod(
        METHOD_DECODE,
        asyncUnaryCall(
          new io.grpc.stub.ServerCalls.UnaryMethod<
              ch.unine.iiun.safecloud.Playcloud.DecodeRequest,
              ch.unine.iiun.safecloud.Playcloud.DecodeReply>() {
            @java.lang.Override
            public void invoke(
                ch.unine.iiun.safecloud.Playcloud.DecodeRequest request,
                io.grpc.stub.StreamObserver<ch.unine.iiun.safecloud.Playcloud.DecodeReply> responseObserver) {
              serviceImpl.decode(request, responseObserver);
            }
          })).build();
  }
}
