package ch.unine.iiun.safecloud.microbench;

import org.apache.commons.cli.*;

import java.util.Random;

public class MicroBench {
    public static final String USAGE = "\n" +
            "Usage: microbench [-s <payload-size>] [-H <host>] [-p <port>] [-r <requests>]\n\n" +
            "Sends a given number of synchronous requests to a GRPC enabled implementing playcloud.proto\n" +
            "Arguments:\n" +
            "\t-h, --help                        Print this help message\n" +
            "\t-H, --host                        Defaults to env variable DUMMY_CODER_PORT_1234_TCP_ADDR or 127.0.0.1\n" +
            "\t-p, --port                        Defaults to env variable DUMMY_CODER_PORT_1234_TCP_PORT or 1234\n" +
            "\t-r, --requests                    Number of requests to send, defaults to 1000\n" +
            "\t-s, --size                        Payload size in bytes, defaults to 1024\n";
    public static final Options OPTIONS = new Options();

    public static final String DEFAULT_HOST = (System.getenv("DUMMY_CODER_PORT_1234_TCP_ADDR") != null) ? System.getenv("DUMMY_CODER_PORT_1234_TCP_ADDR") : "127.0.0.1";
    public static final int DEFAULT_PORT = (System.getenv("DUMMY_CODER_PORT_1234_TCP_PORT") != null) ? Integer.parseInt(System.getenv("DUMMY_CODER_PORT_1234_TCP_PORT")) : 1234;
    public static final int DEFAULT_PAYLOAD_SIZE = 1024;
    public static final int DEFAULT_REQUESTS = 1000;

    static {
        OPTIONS.addOption("h", "help", false, "Help message");
        OPTIONS.addOption("H", "host", true, "Host");
        OPTIONS.addOption("p", "port", true, "Port");
        OPTIONS.addOption("s", "size", true, "Payload size");
        OPTIONS.addOption("r", "requests", true, "Requests");
    }

    static byte[] generateRandomData(final int size) {
        final byte[] data = new byte[size];
        Random random = new Random();
        random.setSeed(System.currentTimeMillis());
        random.nextBytes(data);
        return data;
    }

    public static void main(final String[] args) throws Throwable {
        String host = DEFAULT_HOST;
        int port = DEFAULT_PORT, payloadSize = DEFAULT_PAYLOAD_SIZE, requests = DEFAULT_REQUESTS;
        CommandLineParser parser = new DefaultParser();
        CommandLine command = null;
        try {
            command = parser.parse(OPTIONS, args);
        } catch (ParseException e) {
            e.printStackTrace();
            System.exit(1);
        }

        if (command.hasOption("h")) {
            System.out.println(USAGE);
            System.exit(0);
        }
        if (command.hasOption("H")) {
            host = command.getOptionValue("H");
        }

        if (command.hasOption("p")) {
            int portArgument = -1;
            try {
                portArgument = Integer.parseInt(command.getOptionValue("p"));
            } catch (NumberFormatException e) {
                System.err.println("port argument must be an integer");
                System.exit(1);
            }
            if (portArgument <= 0 || 65536 <= portArgument) {
                System.err.println("port must be greater than 0 and lower than 65536");
                System.exit(1);
            }
            port = portArgument;
        }

        if (command.hasOption("s")) {
            int sizeArgument = -1;
            try {
                sizeArgument = Integer.parseInt(command.getOptionValue("s"));
            } catch (NumberFormatException e) {
                System.err.println("payload size argument must be an integer");
                System.exit(1);
            }
            if (sizeArgument <= 0) {
                System.err.println("payload size argument must be greater than 0");
                System.exit(1);
            }
            payloadSize = sizeArgument;
        }
        
        if (command.hasOption("r")) {
            int requestsArgument = -1;
            try {
                requestsArgument = Integer.parseInt(command.getOptionValue("r"));
            } catch (NumberFormatException e) {
                System.err.println("requests argument must be an integer");
                System.exit(1);
            }
            if (requestsArgument <= 0) {
                System.err.println("requests argument must be greater than 0");
                System.exit(1);
            }
            requests = requestsArgument;
        }

        final byte[] data = generateRandomData(payloadSize);
        System.out.println(requests + " requests will be sent to " + host + ":" + port + " with data of size " + payloadSize + " bytes");
        Client client = new Client(host, port);
        long[] results = new long[requests];
        for (int i = 0; i < requests; i++) {
            results[i] = client.encode(data);
            System.out.println(results[i]);
        }
    }
}
