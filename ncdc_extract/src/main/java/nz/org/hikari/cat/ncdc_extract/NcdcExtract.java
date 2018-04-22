package nz.org.hikari.cat.ncdc_extract;

// Driver for NCDC extract MapReduce job
//
// Args: <station list> <input location ...> <output location>
//
//       e.g. s3://BUCKETNAME/ncdc/stations s3://BUCKETNAME/ncdc/data/ /out
//
//       (note that /out will be created in HDFS, not the local filesystem,
//       and that it must not exist prior to running the job).
//
// Input: NCDC data files, optionally compressed in a MapReduce-compatible
//        format such as gzip or bzip2, and a text file of desired station IDs
//        to extract, one per line
//
// Output: One output file per station containing all the raw input data for
//         that station

import java.net.URI;

import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.LazyOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;

public class NcdcExtract extends Configured implements Tool {

	public int run(String[] args) throws Exception {
		Job job = Job.getInstance(getConf(), "NCDC Extract");
		job.setJarByClass(NcdcExtract.class);
		job.setMapperClass(NcdcExtractMapper.class);
		job.setMapOutputKeyClass(Text.class);
		job.setMapOutputValueClass(Text.class);
		job.setReducerClass(NcdcExtractReducer.class);
		job.setOutputKeyClass(NullWritable.class);
		job.setOutputValueClass(Text.class);

		if (args.length < 3)
			throw new IllegalArgumentException("Insufficient command-line arguments");
		FileInputFormat.setInputDirRecursive(job, true);
		job.addCacheFile(new URI(args[0] + "#" + Constants.LOCAL_STATION_FILE));
		for (int i = 1; i < args.length - 1; i++)
			FileInputFormat.addInputPath(job, new Path(args[i]));
		FileOutputFormat.setOutputPath(job, new Path(args[args.length - 1]));
		LazyOutputFormat.setOutputFormatClass(job, TextOutputFormat.class);

		return job.waitForCompletion(true) ? 0 : 1;
	}

	public static void main(String[] args) throws Exception {
		System.exit(ToolRunner.run(new NcdcExtract(), args));
	}

}
