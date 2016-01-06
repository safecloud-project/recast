package ch.unine.iiun.safecloud;

import static io.grpc.stub.ClientCalls.asyncUnaryCall;
import static io.grpc.stub.ClientCalls.blockingUnaryCall;
import static io.grpc.stub.ClientCalls.futureUnaryCall;
import static io.grpc.MethodDescriptor.generateFullMethodName;
import static io.grpc.stub.ServerCalls.asyncUnaryCall;

@javax.annotation.Generated("by gRPC proto compiler")
public class EncoderDecoderGrpc {

  private EncoderDecoderGrpc() {}

  public static final String SERVICE_NAME = "EncoderDecoder";

  // Static method descriptors that strictly reflect the proto.
  @io.grpc.ExperimentalApi
  public static final io.grpc.MethodDescriptor<Playcloud.EncodeRequest,
      Playcloud.EncodeReply> METHOD_ENCODE =
      io.grpc.MethodDescriptor.create(
          io.grpc.MethodDescriptor.MethodType.UNARY,
          generateFullMethodName(
              "EncoderDecoder", "Encode"),
          io.grpc.protobuf.ProtoUtils.marshaller(Playcloud.EncodeRequest.getDefaultInstance()),
          io.grpc.protobuf.ProtoUtils.marshaller(Playcloud.EncodeReply.getDefaultInstance()));
  @io.grpc.ExperimentalApi
  public static final io.grpc.MethodDescriptor<Playcloud.DecodeRequest,
      Playcloud.DecodeReply> METHOD_DECODE =
      io.grpc.MethodDescriptor.create(
          io.grpc.MethodDescriptor.MethodType.UNARY,
          generateFullMethodName(
              "EncoderDecoder", "Decode"),
          io.grpc.protobuf.ProtoUtils.marshaller(Playcloud.DecodeRequest.getDefaultInstance()),
          io.grpc.protobuf.ProtoUtils.marshaller(Playcloud.DecodeReply.getDefaultInstance()));

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

    public void encode(Playcloud.EncodeRequest request,
        io.grpc.stub.StreamObserver<Playcloud.EncodeReply> responseObserver);

    public void decode(Playcloud.DecodeRequest request,
        io.grpc.stub.StreamObserver<Playcloud.DecodeReply> responseObserver);
  }

  public static interface EncoderDecoderBlockingClient {

    public Playcloud.EncodeReply encode(Playcloud.EncodeRequest request);

    public Playcloud.DecodeReply decode(Playcloud.DecodeRequest request);
  }

  public static interface EncoderDecoderFutureClient {

    public com.google.common.util.concurrent.ListenableFuture<Playcloud.EncodeReply> encode(
        Playcloud.EncodeRequest request);

    public com.google.common.util.concurrent.ListenableFuture<Playcloud.DecodeReply> decode(
        Playcloud.DecodeRequest request);
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
    public void encode(Playcloud.EncodeRequest request,
        io.grpc.stub.StreamObserver<Playcloud.EncodeReply> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(METHOD_ENCODE, getCallOptions()), request, responseObserver);
    }

    @java.lang.Override
    public void decode(Playcloud.DecodeRequest request,
        io.grpc.stub.StreamObserver<Playcloud.DecodeReply> responseObserver) {
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
    public Playcloud.EncodeReply encode(Playcloud.EncodeRequest request) {
      return blockingUnaryCall(
          getChannel().newCall(METHOD_ENCODE, getCallOptions()), request);
    }

    @java.lang.Override
    public Playcloud.DecodeReply decode(Playcloud.DecodeRequest request) {
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
    public com.google.common.util.concurrent.ListenableFuture<Playcloud.EncodeReply> encode(
        Playcloud.EncodeRequest request) {
      return futureUnaryCall(
          getChannel().newCall(METHOD_ENCODE, getCallOptions()), request);
    }

    @java.lang.Override
    public com.google.common.util.concurrent.ListenableFuture<Playcloud.DecodeReply> decode(
        Playcloud.DecodeRequest request) {
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
              Playcloud.EncodeRequest,
              Playcloud.EncodeReply>() {
            @java.lang.Override
            public void invoke(
                Playcloud.EncodeRequest request,
                io.grpc.stub.StreamObserver<Playcloud.EncodeReply> responseObserver) {
              serviceImpl.encode(request, responseObserver);
            }
          }))
      .addMethod(
        METHOD_DECODE,
        asyncUnaryCall(
          new io.grpc.stub.ServerCalls.UnaryMethod<
              Playcloud.DecodeRequest,
              Playcloud.DecodeReply>() {
            @java.lang.Override
            public void invoke(
                Playcloud.DecodeRequest request,
                io.grpc.stub.StreamObserver<Playcloud.DecodeReply> responseObserver) {
              serviceImpl.decode(request, responseObserver);
            }
          })).build();
  }
}
