"""Conservative source selection; never replace a chosen source with another device."""
import math


def stream_key(info):
    # uid changes when an outlet restarts; source_id + host identifies the device.
    source = info.source_id()
    return (info.hostname(), source) if source else (info.hostname(), info.uid())


def candidates(streams):
    return [s for s in streams if s.channel_count() > 0
            and math.isfinite(s.nominal_srate()) and s.nominal_srate() > 0
            and s.channel_format() in (1, 2, 3, 4, 5, 7)
            and not s.source_id().startswith('DEMO_')]


def choose_stream(streams, remembered=None):
    eligible = candidates(streams)
    if remembered is not None:
        eligible = [s for s in eligible if stream_key(s) == remembered]
    return eligible[0] if len(eligible) == 1 else None


def metadata_signature(meta):
    return tuple(meta.get(k) if k not in ('labels', 'units') else tuple(meta.get(k, []))
                 for k in ('channel_count', 'nominal_srate', 'channel_format', 'labels', 'units'))
