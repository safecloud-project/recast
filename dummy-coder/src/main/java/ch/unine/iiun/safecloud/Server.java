package ch.unine.iiun.safecloud;

import io.grpc.internal.ServerImpl;
import io.grpc.netty.NettyServerBuilder;

import java.io.IOException;
import java.util.Scanner;
import java.util.logging.Logger;

public class Server {

    public final static int DEFAULT_PORT = 1234;

    private int port;
    private Logger logger = Logger.getLogger(Server.class.getSimpleName());
    private ServerImpl gRpcServer;

    public Server() {
        Server(DEFAULT_PORT);
    }

    public void Server(int port) {
        this.port = port;
    }

    public void start() throws IOException {
        try {
            gRpcServer = NettyServerBuilder.forPort(this.port)
                    .addService(EncoderDecoderGrpc.bindService(new EncoderDecoderService()))
                    .build().start();
        } catch (IOException e) {
            logger.severe(e.getMessage());
            throw e;
        }
        logger.info("Server started, listening on " + this.port);
    }

    public void stop() {
        gRpcServer.shutdownNow();
    }
}
