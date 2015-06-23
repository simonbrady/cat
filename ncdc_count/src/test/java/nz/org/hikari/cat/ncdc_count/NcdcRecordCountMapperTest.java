package nz.org.hikari.cat.ncdc_count;

import java.io.IOException;

import nz.org.hikari.cat.ncdc_count.NcdcRecordCountMapper;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mrunit.mapreduce.MapDriver;
import org.junit.*;

// MRUnit test class for NcdcRecordCountMapper
//
// Based on the example in Tom White, "Hadoop: The Definitive Guide" (3rd ed:
// O'Reilly, 2012), p154, but updated for MRUnit 1.10

public class NcdcRecordCountMapperTest {

	@Test
	public void processValidRecord() throws IOException, InterruptedException {
		// Dummy offset
		LongWritable key = new LongWritable(0L);
		// First record in 1901/029070-99999-1901.gz
		Text value = new Text("0029029070999991901010106004+64333+023450FM-12"
			+ "+000599999V0202701N015919999999N0000001N9-00781+99999102001"
			+ "ADDGF108991999999999999999999");
		new MapDriver<LongWritable, Text, Text, LongWritable>()
			.withMapper(new NcdcRecordCountMapper())
			.withInput(key, value)
			.withOutput(new Text("029070-99999"), new LongWritable(1L))
			.runTest();
	}

}
