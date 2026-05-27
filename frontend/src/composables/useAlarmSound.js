// Generates alarm tones via Web Audio API — no external files required.
// Three patterns with distinct urgency levels.

const PATTERNS = {
  gentle: {
    // Three soft ascending notes, repeat every 5 s
    notes: [
      { freq: 440, start: 0.00, vol: 0.25 },
      { freq: 550, start: 0.45, vol: 0.25 },
      { freq: 660, start: 0.90, vol: 0.25 },
    ],
    duration: 1.4,
    pause: 5_000,
  },
  default: {
    // Five beeps at 880 Hz, repeat every 3 s
    notes: [
      { freq: 880, start: 0.00, vol: 0.5 },
      { freq: 880, start: 0.35, vol: 0.5 },
      { freq: 880, start: 0.70, vol: 0.5 },
      { freq: 880, start: 1.10, vol: 0.5 },
      { freq: 880, start: 1.45, vol: 0.5 },
    ],
    duration: 1.8,
    pause: 3_000,
  },
  urgent: {
    // Rapid alternating 880 / 1100 Hz, repeat every 2 s
    notes: [
      { freq:  880, start: 0.00, vol: 0.7 },
      { freq: 1100, start: 0.18, vol: 0.7 },
      { freq:  880, start: 0.36, vol: 0.7 },
      { freq: 1100, start: 0.54, vol: 0.7 },
      { freq:  880, start: 0.72, vol: 0.7 },
      { freq: 1100, start: 0.90, vol: 0.7 },
      { freq:  880, start: 1.08, vol: 0.7 },
      { freq: 1100, start: 1.26, vol: 0.7 },
    ],
    duration: 1.5,
    pause: 2_000,
  },
}

export function useAlarmSound() {
  let ctx      = null
  let timer    = null
  let playing  = false

  function _playOnce(pattern) {
    if (!ctx || !playing) return
    const base = ctx.currentTime + 0.05
    pattern.notes.forEach(({ freq, start, vol }) => {
      const osc  = ctx.createOscillator()
      const gain = ctx.createGain()
      osc.connect(gain)
      gain.connect(ctx.destination)
      osc.type = 'sine'
      osc.frequency.value = freq
      const t = base + start
      gain.gain.setValueAtTime(0, t)
      gain.gain.linearRampToValueAtTime(vol, t + 0.015)
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.22)
      osc.start(t)
      osc.stop(t + 0.25)
    })
  }

  function play(type = 'default') {
    if (playing) return
    playing = true
    try {
      ctx = new (window.AudioContext || window.webkitAudioContext)()
    } catch {
      return // audio not supported
    }
    const pattern = PATTERNS[type] || PATTERNS.default

    const loop = () => {
      if (!playing) return
      _playOnce(pattern)
      timer = setTimeout(loop, pattern.pause)
    }
    loop()
  }

  function stop() {
    playing = false
    if (timer) { clearTimeout(timer); timer = null }
    if (ctx)   { ctx.close().catch(() => {}); ctx = null }
  }

  return { play, stop }
}
