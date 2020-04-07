import java.io.BufferedWriter;
import java.io.FileWriter;

public class GenTestFile {
	public static void main(final String args[]) throws Exception {
		try (BufferedWriter writer = new BufferedWriter(new FileWriter("maintenance_data.txt"))) {
			for (int i = 0; i < 1024 * 1024 * 160; i++) {
				writer.write("1");
			}
		}
	}
}
