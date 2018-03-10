package nz.org.hikari.cat.ncdc_download;

import java.util.Map;
import java.util.Map.Entry;
import java.util.TreeMap;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;

// Print Hadoop configuration, taken from Tom White, "Hadoop: The Definitive Guide"
// (4th ed, O'Reilly, 2015), p. 149

public class ConfigurationPrinter extends Configured implements Tool {

	static {
		Configuration.addDefaultResource("hdfs-default.xml");
		Configuration.addDefaultResource("hdfs-site.xml");
		Configuration.addDefaultResource("mapred-default.xml");
		Configuration.addDefaultResource("mapred-site.xml");
		Configuration.addDefaultResource("yarn-default.xml");
		Configuration.addDefaultResource("yarn-site.xml");
	}

	@Override
	public int run(String[] args) throws Exception {
		Configuration conf = getConf();
		Map<String, String> map = new TreeMap<>();
		for (Entry<String, String> entry : conf) {
			map.put(entry.getKey(), entry.getValue());
		}
		for (Entry<String, String> entry : map.entrySet()) {
			System.out.printf("%s=%s\n", entry.getKey(), entry.getValue());
		}
		return 0;
	}

	public static void main(String[] args) throws Exception {
		System.exit(ToolRunner.run(new ConfigurationPrinter(), args));
	}

}
