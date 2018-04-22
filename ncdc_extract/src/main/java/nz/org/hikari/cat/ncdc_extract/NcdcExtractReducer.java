package nz.org.hikari.cat.ncdc_extract;

// Reducer for NCDC extract MapReduce job, called from NcdcExtract driver class

import java.io.IOException;

import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.output.MultipleOutputs;

public class NcdcExtractReducer
		extends Reducer<Text, Text, NullWritable, Text> {

	private MultipleOutputs<NullWritable, Text> multipleOutputs;

	@Override
	protected void setup(Context context) throws IOException {
		multipleOutputs = new MultipleOutputs<>(context);
	}

	@Override
	public void reduce(Text key, Iterable<Text> values, Context context)
			throws IOException, InterruptedException {
		String id = key.toString();
		for (Text value : values) {
			multipleOutputs.write(NullWritable.get(), value, id);
			context.getCounter(Constants.COUNTER_GROUP, id).increment(1);
		}
	}

	@Override
	protected void cleanup(Context context) throws IOException, InterruptedException {
		multipleOutputs.close();
	}

}
