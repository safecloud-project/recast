package ch.unine.iiun.safecloud;

import java.io.IOException;
import java.util.Scanner;

public class Main {

    public static void main(String[] args) throws IOException {
        Server server = new Server();
        server.start();
        Scanner scanner = new Scanner(System.in);
        while (scanner.hasNext()) ;
        server.stop();
        System.exit(0);
    }
}
