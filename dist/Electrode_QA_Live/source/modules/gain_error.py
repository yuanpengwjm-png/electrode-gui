"""AmplitudePeakGainError: calibrated sine peak-to-peak amplitude versus input."""
from models import MetricResult


class AmplitudePeakGainError:
    def __init__(self, settings):
        self.settings = settings

    def evaluate(self, fit, record):
        measured = fit["amplitude_pp_mV"]
        error = None if measured is None or record.input_mVpp is None else 100*(measured/record.input_mVpp-1)
        values = dict(output_mVpp=measured, input_mVpp=record.input_mVpp, gain_error_pct=error,
                      input_confirmed=record.input_confirmed, quality_reasons=fit["quality_reasons"])
        if any(reason in fit["quality_reasons"] for reason in ("no_reliable_sine_response", "no_reliable_pulse_response")):
            return MetricResult("red", "No reliable response; check the electrode path and input", values)
        if fit["quality_reasons"]:
            return MetricResult("yellow", "Waveform quality is insufficient; repeat the gain test: "+", ".join(fit["quality_reasons"]), values)
        if record.input_mVpp is None or not record.input_confirmed:
            return MetricResult("yellow", "Actual input Vpp is unconfirmed; absolute gain cannot be assessed", values)
        color = self.settings.color(error, self.settings.gain_limit_pct)
        kind = "low" if error < 0 else "high"
        label = "within limits" if color == "green" else ("near the limit" if color == "yellow" else kind+"; check required")
        return MetricResult(color, f"Gain {error:+.3f}%: {label}", values)
