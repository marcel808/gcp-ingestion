package com.mozilla.telemetry.options;

import com.mozilla.telemetry.Sink;
import org.apache.beam.sdk.io.gcp.pubsub.PubsubMessage;
import org.apache.beam.sdk.transforms.PTransform;
import org.apache.beam.sdk.values.PCollection;
import org.apache.beam.sdk.values.PDone;

/**
 * Enumeration of error output types that each provide a {@code write} method.
 */
public enum ErrorOutputType {
  stdout {
    /** Return a PTransform that prints errors to STDOUT; only for local running. */
    public PTransform<PCollection<PubsubMessage>, PDone> write(
        Sink.Options options
    ) {
      return OutputType.print(FORMAT, System.out::println);
    }
  },

  stderr {
    /** Return a PTransform that prints errors to STDERR; only for local running. */
    public PTransform<PCollection<PubsubMessage>, PDone> write(
        Sink.Options options
    ) {
      return OutputType.print(FORMAT, System.err::println);
    }
  },

  file {
    /** Return a PTransform that writes errors to local or remote files. */
    public PTransform<PCollection<PubsubMessage>, PDone> write(
        Sink.Options options
    ) {
      return OutputType.writeFiles(options.getErrorOutput(), FORMAT, options.getWindowDuration());
    }
  },

  pubsub {
    /** Return a PTransform that writes to Google Pubsub. */
    public PTransform<PCollection<PubsubMessage>, PDone> write(
        Sink.Options options
    ) {
      return OutputType.writePubsub(options.getErrorOutput());
    }
  };

  public static OutputFileFormat FORMAT = OutputFileFormat.json;

  public abstract PTransform<PCollection<PubsubMessage>, PDone> write(
      Sink.Options options
  );
}