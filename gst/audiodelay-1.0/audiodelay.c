/* 
 * GStreamer
 * Copyright (C) 2009 Sebastian Dröge <sebastian.droege@collabora.co.uk>
 * Copyright (C) 2014 IOhannes m zmölnig <zmoelnig@iem.at>
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library;
 * If not, see <http://www.gnu.org/licenses/>.
 */

/**
 * SECTION:element-audiodelay
 *
 * audiodelay adds a delay effect to an audio stream.
 * Only the delay can be configured.
 *
 * Use the max-delay property to set the maximum amount of delay that
 * will be used. This can only be set before going to the PAUSED or PLAYING
 * state and will be set to the current delay by default.
 *
 * <refsect2>
 * <title>Example launch line</title>
 * |[
 * gst-launch-1.0 filesrc location="melo1.ogg" ! audioconvert ! audiodelay delay=500000000 ! audioconvert ! autoaudiosink
 * gst-launch-1.0 filesrc location="melo1.ogg" ! decodebin ! audioconvert ! audiodelay delay=50000000 ! audioconvert ! autoaudiosink
 * ]|
 * </refsect2>
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gst/gst.h>
#include <gst/base/gstbasetransform.h>
#include <gst/audio/audio.h>
#include <gst/audio/gstaudiofilter.h>

#include "audiodelay.h"

#define GST_CAT_DEFAULT gst_audio_delay_debug
GST_DEBUG_CATEGORY_STATIC (GST_CAT_DEFAULT);

enum
  {
    PROP_0,
    PROP_DELAY,
    PROP_MAX_DELAY
  };

#define ALLOWED_CAPS							\
  "audio/x-raw,"							\
  " format=(string) {"GST_AUDIO_NE(F32)","GST_AUDIO_NE(F64)"}, "	\
  " rate=(int)[1,MAX],"							\
  " channels=(int)[1,MAX],"						\
  " layout=(string) interleaved"

#define gst_audio_delay_parent_class parent_class
G_DEFINE_TYPE (GstAudioDelay, gst_audio_delay, GST_TYPE_AUDIO_FILTER);

static void gst_audio_delay_set_property (GObject * object, guint prop_id,
					  const GValue * value, GParamSpec * pspec);
static void gst_audio_delay_get_property (GObject * object, guint prop_id,
					  GValue * value, GParamSpec * pspec);
static void gst_audio_delay_finalize (GObject * object);

static gboolean gst_audio_delay_setup (GstAudioFilter * self,
				       const GstAudioInfo * info);
static gboolean gst_audio_delay_stop (GstBaseTransform * base);
static GstFlowReturn gst_audio_delay_transform_ip (GstBaseTransform * base,
						   GstBuffer * buf);

static void gst_audio_delay_transform_float (GstAudioDelay * self,
					     gfloat * data, guint num_samples);
static void gst_audio_delay_transform_double (GstAudioDelay * self,
					      gdouble * data, guint num_samples);

/* GObject vmethod implementations */

static void
gst_audio_delay_class_init (GstAudioDelayClass * klass)
{
  GObjectClass *gobject_class = (GObjectClass *) klass;
  GstElementClass *gstelement_class = (GstElementClass *) klass;
  GstBaseTransformClass *basetransform_class = (GstBaseTransformClass *) klass;
  GstAudioFilterClass *audioself_class = (GstAudioFilterClass *) klass;
  GstCaps *caps;

  GST_DEBUG_CATEGORY_INIT (gst_audio_delay_debug, "audiodelay", 0,
			   "audiodelay element");

  gobject_class->set_property = gst_audio_delay_set_property;
  gobject_class->get_property = gst_audio_delay_get_property;
  gobject_class->finalize = gst_audio_delay_finalize;

  g_object_class_install_property (gobject_class, PROP_DELAY,
				   g_param_spec_uint64 ("delay", "Delay",
							"Delay of the delay in nanoseconds", 1, G_MAXUINT64,
							1, G_PARAM_READWRITE | G_PARAM_STATIC_STRINGS
							| GST_PARAM_CONTROLLABLE));

  g_object_class_install_property (gobject_class, PROP_MAX_DELAY,
				   g_param_spec_uint64 ("max-delay", "Maximum Delay",
							"Maximum delay of the delay in nanoseconds"
							" (can't be changed in PLAYING or PAUSED state)",
							1, G_MAXUINT64, 1,
							G_PARAM_READWRITE | G_PARAM_STATIC_STRINGS |
							GST_PARAM_MUTABLE_READY));

  gst_element_class_set_static_metadata (gstelement_class, "Audio delay",
					 "Filter/Effect/Audio",
					 "Adds a delay to an audio stream",
					 "IOhannes m zmölnig <zmoelnig@iem.at>");

  caps = gst_caps_from_string (ALLOWED_CAPS);
  gst_audio_filter_class_add_pad_templates (GST_AUDIO_FILTER_CLASS (klass),
					    caps);
  gst_caps_unref (caps);

  audioself_class->setup = GST_DEBUG_FUNCPTR (gst_audio_delay_setup);
  basetransform_class->transform_ip =
    GST_DEBUG_FUNCPTR (gst_audio_delay_transform_ip);
  basetransform_class->stop = GST_DEBUG_FUNCPTR (gst_audio_delay_stop);
}

static void
gst_audio_delay_init (GstAudioDelay * self)
{
  self->delay = 1;
  self->max_delay = 1;

  g_mutex_init (&self->lock);

  gst_base_transform_set_in_place (GST_BASE_TRANSFORM (self), TRUE);
}

static void
gst_audio_delay_finalize (GObject * object)
{
  GstAudioDelay *self = GST_AUDIO_DELAY (object);

  g_free (self->buffer);
  self->buffer = NULL;

  g_mutex_clear (&self->lock);

  G_OBJECT_CLASS (parent_class)->finalize (object);
}

static void
gst_audio_delay_set_property (GObject * object, guint prop_id,
			      const GValue * value, GParamSpec * pspec)
{
  GstAudioDelay *self = GST_AUDIO_DELAY (object);

  switch (prop_id) {
  case PROP_DELAY:{
    guint64 max_delay, delay;
    guint rate;

    g_mutex_lock (&self->lock);
    delay = g_value_get_uint64 (value);
    max_delay = self->max_delay;

    if (delay > max_delay && GST_STATE (self) > GST_STATE_READY) {
      GST_WARNING_OBJECT (self, "New delay (%" GST_TIME_FORMAT ") "
			  "is larger than maximum delay (%" GST_TIME_FORMAT ")",
			  GST_TIME_ARGS (delay), GST_TIME_ARGS (max_delay));
      self->delay = max_delay;
    } else {
      self->delay = delay;
      self->max_delay = MAX (delay, max_delay);
    }
    rate = GST_AUDIO_FILTER_RATE (self);
    if (rate > 0)
      self->delay_frames =
	MAX (gst_util_uint64_scale (self->delay, rate, GST_SECOND), 1);

    g_mutex_unlock (&self->lock);
    break;
  }
  case PROP_MAX_DELAY:{
    guint64 max_delay, delay;

    g_mutex_lock (&self->lock);
    max_delay = g_value_get_uint64 (value);
    delay = self->delay;

    if (GST_STATE (self) > GST_STATE_READY) {
      GST_ERROR_OBJECT (self, "Can't change maximum delay in"
			" PLAYING or PAUSED state");
    } else {
      self->delay = delay;
      self->max_delay = max_delay;
    }
    g_mutex_unlock (&self->lock);
    break;
  }
  default:
    G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
    break;
  }
}

static void
gst_audio_delay_get_property (GObject * object, guint prop_id,
			      GValue * value, GParamSpec * pspec)
{
  GstAudioDelay *self = GST_AUDIO_DELAY (object);

  switch (prop_id) {
  case PROP_DELAY:
    g_mutex_lock (&self->lock);
    g_value_set_uint64 (value, self->delay);
    g_mutex_unlock (&self->lock);
    break;
  case PROP_MAX_DELAY:
    g_mutex_lock (&self->lock);
    g_value_set_uint64 (value, self->max_delay);
    g_mutex_unlock (&self->lock);
    break;
  default:
    G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
    break;
  }
}

/* GstAudioFilter vmethod implementations */

static gboolean
gst_audio_delay_setup (GstAudioFilter * base, const GstAudioInfo * info)
{
  GstAudioDelay *self = GST_AUDIO_DELAY (base);
  gboolean ret = TRUE;

  switch (GST_AUDIO_INFO_FORMAT (info)) {
  case GST_AUDIO_FORMAT_F32:
    self->process = (GstAudioDelayProcessFunc)
      gst_audio_delay_transform_float;
    break;
  case GST_AUDIO_FORMAT_F64:
    self->process = (GstAudioDelayProcessFunc)
      gst_audio_delay_transform_double;
    break;
  default:
    ret = FALSE;
    break;
  }

  g_free (self->buffer);
  self->buffer = NULL;
  self->buffer_pos = 0;
  self->buffer_size = 0;
  self->buffer_size_frames = 0;

  return ret;
}

static gboolean
gst_audio_delay_stop (GstBaseTransform * base)
{
  GstAudioDelay *self = GST_AUDIO_DELAY (base);

  g_free (self->buffer);
  self->buffer = NULL;
  self->buffer_pos = 0;
  self->buffer_size = 0;
  self->buffer_size_frames = 0;

  return TRUE;
}

#define TRANSFORM_FUNC(name, type)					\
  static void								\
  gst_audio_delay_transform_##name (GstAudioDelay * self,		\
				    type * data, guint num_samples)	\
  {									\
    type *buffer = (type *) self->buffer;				\
    guint channels = GST_AUDIO_FILTER_CHANNELS (self);			\
    guint rate = GST_AUDIO_FILTER_RATE (self);				\
    guint i, j;								\
    guint delay_index = self->buffer_size_frames - self->delay_frames;	\
    gdouble delay_off = ((((gdouble) self->delay) * rate) / GST_SECOND) - self->delay_frames; \
									\
    if (delay_off < 0.0)						\
      delay_off = 0.0;							\
									\
    num_samples /= channels;						\
									\
    for (i = 0; i < num_samples; i++) {					\
      guint delay0_index = ((delay_index + self->buffer_pos) % self->buffer_size_frames) * channels; \
      guint delay1_index = ((delay_index + self->buffer_pos +1) % self->buffer_size_frames) * channels; \
      guint rbout_index = (self->buffer_pos % self->buffer_size_frames) * channels; \
      for (j = 0; j < channels; j++) {					\
	gdouble in = data[i*channels + j];				\
	gdouble delay0 = buffer[delay0_index + j];			\
	gdouble delay1 = buffer[delay1_index + j];			\
	gdouble delay = delay0 + (delay1-delay0)*delay_off;		\
	type out = delay;						\
									\
	data[i*channels + j] = out;					\
	buffer[rbout_index + j] = in;					\
      }									\
      self->buffer_pos = (self->buffer_pos + 1) % self->buffer_size_frames; \
    }									\
  }

TRANSFORM_FUNC (float, gfloat);
TRANSFORM_FUNC (double, gdouble);

/* GstBaseTransform vmethod implementations */
static GstFlowReturn
gst_audio_delay_transform_ip (GstBaseTransform * base, GstBuffer * buf)
{
  GstAudioDelay *self = GST_AUDIO_DELAY (base);
  guint num_samples;
  GstClockTime timestamp, stream_time;
  GstMapInfo map;

  g_mutex_lock (&self->lock);
  timestamp = GST_BUFFER_TIMESTAMP (buf);
  stream_time =
    gst_segment_to_stream_time (&base->segment, GST_FORMAT_TIME, timestamp);

  GST_DEBUG_OBJECT (self, "sync to %" GST_TIME_FORMAT,
		    GST_TIME_ARGS (timestamp));

  if (GST_CLOCK_TIME_IS_VALID (stream_time))
    gst_object_sync_values (GST_OBJECT (self), stream_time);

  if (self->buffer == NULL) {
    guint bpf, rate;

    bpf = GST_AUDIO_FILTER_BPF (self);
    rate = GST_AUDIO_FILTER_RATE (self);

    self->delay_frames =
      MAX (gst_util_uint64_scale (self->delay, rate, GST_SECOND), 1);
    self->buffer_size_frames =
      MAX (gst_util_uint64_scale (self->max_delay, rate, GST_SECOND), 1);

    self->buffer_size = self->buffer_size_frames * bpf;
    self->buffer = g_try_malloc0 (self->buffer_size);
    self->buffer_pos = 0;

    if (self->buffer == NULL) {
      g_mutex_unlock (&self->lock);
      GST_ERROR_OBJECT (self, "Failed to allocate %u bytes", self->buffer_size);
      return GST_FLOW_ERROR;
    }
  }

  gst_buffer_map (buf, &map, GST_MAP_READWRITE);
  num_samples = map.size / GST_AUDIO_FILTER_BPS (self);

  self->process (self, map.data, num_samples);

  gst_buffer_unmap (buf, &map);
  g_mutex_unlock (&self->lock);

  return GST_FLOW_OK;
}



/* entry point to initialize the plug-in
 * initialize the plug-in itself
 * register the element factories and pad templates
 * register the features
 */
static gboolean
plugin_init (GstPlugin * plugin)
{
  return (gst_element_register (plugin, "audiodelay", GST_RANK_NONE,
				GST_TYPE_AUDIO_DELAY)
	  );
}
#ifndef PACKAGE
# define PACKAGE "striem"
#endif
GST_PLUGIN_DEFINE (GST_VERSION_MAJOR,
		   GST_VERSION_MINOR,
		   audiodelay,
		   "Audio delay plugin",
		   plugin_init, "0.0", "LGPL", "striem", "http://striem.iem.at")
