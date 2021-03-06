package nz.org.hikari.cat.ncdc_extract;

// Unit tests for NcdcExtractMapper

import static org.junit.Assert.assertEquals;
import static org.mockito.Mockito.*;

import java.io.BufferedReader;
import java.io.StringReader;
import java.lang.reflect.Method;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Counter;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.mockito.junit.MockitoJUnitRunner;

@RunWith(MockitoJUnitRunner.class)
public class NcdcExtractMapperTest {

	private NcdcExtractMapper mapper;

	@Mock
	private NcdcExtractMapper.Context context;

	@Mock
	private Counter extractedCounter;

	@Mock
	private Counter ignoredCounter;

	@Before
	public void setUp() throws Exception {
		mapper = new NcdcExtractMapper();
	}

	@Test
	public void testMap() throws Exception {
		// Station to extract
		String station = "029070-99999";
		Text key = new Text(station);
		// Simulated file of station IDs, including comments and blank lines
		String stationInput = String.format("# foo\n\n  \n%s bar\n\t#\n", station);
		// Dummy offset
		LongWritable dummy = new LongWritable(0L);
		// Control data section of first record in 1901/029070-99999-1901.gz
		Text value1 = new Text("0029029070999991901010106004+64333+023450FM-12+000599999V020");
		// Control data section of first record in 1901/029500-99999-1901.gz
		Text value2 = new Text("0029029500999991901010106004+61483+021350FM-12+000699999V020");
		// Control data section of second record in 1901/029070-99999-1901.gz
		Text value3 = new Text("0029029070999991901010113004+64333+023450FM-12+000599999V020");

		when(context.getCounter(Constants.COUNTER_GROUP, Constants.EXTRACTED))
			.thenReturn(extractedCounter);
		when(context.getCounter(Constants.COUNTER_GROUP, Constants.IGNORED))
			.thenReturn(ignoredCounter);

		// Simulate call to mapper.setup()
		Method mapperReadStations = NcdcExtractMapper.class
			.getDeclaredMethod("readStations", BufferedReader.class);
		mapperReadStations.setAccessible(true);
		mapperReadStations.invoke(mapper, new BufferedReader(new StringReader(stationInput)));
		assertEquals(1, mapper.getNumberOfStations());

		mapper.map(dummy, value1, context);
		mapper.map(dummy, value2, context);
		mapper.map(dummy, value3, context);

		verify(context, times(3)).getCounter(eq(Constants.COUNTER_GROUP), anyString());
		verify(context).write(key, value1);
		verify(context).write(key, value3);
		verify(extractedCounter, times(2)).increment(1);
		verify(ignoredCounter, times(1)).increment(1);
	}

	@After
	public void tearDown() throws Exception {
		verifyNoMoreInteractions(context);
		verifyNoMoreInteractions(extractedCounter);
		verifyNoMoreInteractions(ignoredCounter);
	}

}
