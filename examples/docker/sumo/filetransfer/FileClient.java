import java.io.BufferedOutputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.InetAddress;
import java.net.Socket;
import java.net.ConnectException;

public class FileClient {

	public final static int SOCKET_PORT = 1337;
	public final static String SERVER = "switch";
	public final static String FILE_TO_RECEIVED = "maintenance_data.txt";
	public final static int FILE_SIZE = 162914560;

	public static void main(final String[] args) throws IOException {
		int bytesRead;
		int current = 0;
		FileOutputStream fos = null;
		BufferedOutputStream bos = null;
		Socket sock = null;
		boolean connected = false;
		boolean transmitted = false;
		while(!connected) {
		try {
			while (!InetAddress.getByName(SERVER).isReachable(500)) {
				System.out.println("not reachable");
			}
			sock = new Socket(SERVER, SOCKET_PORT);
			sock.setSoTimeout(2000);
			System.out.println("Connecting...");
			connected = true;

			// receive file
			final byte[] mybytearray = new byte[FILE_SIZE];
			final InputStream is = sock.getInputStream();
			fos = new FileOutputStream(FILE_TO_RECEIVED);
			bos = new BufferedOutputStream(fos);
			bytesRead = is.read(mybytearray, 0, mybytearray.length);
			current = bytesRead;

			do {
				bytesRead = is.read(mybytearray, current, mybytearray.length - current);
				if (bytesRead >= 0) {
					current += bytesRead;
					System.out.println("So far Read: "+current+" bytes");
				}
			} while (bytesRead > -1);

			bos.write(mybytearray, 0, current);
			bos.flush();
			System.out.println("File " + FILE_TO_RECEIVED + " downloaded (" + current + " bytes read)");
			transmitted = true;
		} catch (ConnectException e) {
			System.out.println("Connection not possible");
		} catch (Exception e){
			System.out.println("Connection interrupted");
		} finally {
			if (fos != null) {
				fos.close();
			}
			if (bos != null) {
				bos.close();
			}
			if (sock != null) {
				sock.close();
			}
		}
		}
		if(transmitted){
			System.out.println("Transmission was successful!");
			System.out.println(current + " bytes read.");
		} else {
			System.out.println("Transmission was NOT successful!");
			System.out.println("Only " + current + " bytes read.");
		}
	}

}
