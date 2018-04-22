package nz.org.hikari.cat.ncdc_extract;

// Mapper for NCDC extract MapReduce job, called from NcdcExtract driver class

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashSet;
import java.util.Set;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

public class NcdcExtractMapper
		extends Mapper<LongWritable, Text, Text, Text> {

	private Set<String> stations = new HashSet<>();

	@Override
	protected void setup(Context context) throws IOException {
		readStations(new BufferedReader(new FileReader(Constants.LOCAL_STATION_FILE)));
	}

	// Get set of station IDs to extract, separated out for ease of testing
	private void readStations(BufferedReader reader) throws IOException {
		String line = reader.readLine();
		while (line != null) {
			line = line.trim();
			if (line.length() > 0 && !line.startsWith("#"))
				stations.add(line.split("\\s")[0]);
			line = reader.readLine();
		}
	}

	// Helper for testing
	public int getNumberOfStations() {
		return stations.size();
	}

	@Override
	public void map(LongWritable key, Text value, Context context)
			throws IOException, InterruptedException {
		String line = value.toString();
		String id = line.substring(4, 10) + "-" + line.substring(10, 15);
		if (stations.contains(id)) {
			context.write(new Text(id), value);
			context.getCounter(Constants.COUNTER_GROUP, Constants.EXTRACTED).increment(1);
		} else {
			context.getCounter(Constants.COUNTER_GROUP, Constants.IGNORED).increment(1);
		}
	}

}
