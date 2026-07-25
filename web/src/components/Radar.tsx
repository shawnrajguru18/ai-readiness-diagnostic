import { Dimension } from '@/types'

interface RadarProps {
  dims: Dimension[]
  color: string
  size?: number
}

export function Radar({ dims, color, size = 360 }: RadarProps) {
  const n = dims.length
  const cx = size / 2
  const cy = size / 2
  const R = size * 0.34

  const pt = (i: number, frac: number): [number, number] => {
    const a = (2 * Math.PI * i) / n - Math.PI / 2
    return [cx + R * frac * Math.cos(a), cy + R * frac * Math.sin(a)]
  }

  const ring = (t: number) =>
    dims.map((_, i) => pt(i, t).join(',')).join(' ')

  const you = dims.map((d, i) => pt(i, d.score / 100).join(',')).join(' ')

  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      className="fade"
    >
      {[0.25, 0.5, 0.75, 1].map((t, k) => (
        <polygon
          key={k}
          points={ring(t)}
          fill="none"
          stroke="#D9D5CE"
          strokeWidth="1"
        />
      ))}
      {dims.map((_, i) => {
        const [x, y] = pt(i, 1)
        return (
          <line key={i} x1={cx} y1={cy} x2={x} y2={y} stroke="#E6E1DA" />
        )
      })}
      <polygon points={you} fill={color + '55'} stroke={color} strokeWidth="2.5" />
      {dims.map((d, i) => {
        const [x, y] = pt(i, d.score / 100)
        return (
          <circle
            key={i}
            cx={x}
            cy={y}
            r="3.5"
            fill={color}
            stroke="#0E1020"
            strokeWidth="1"
          />
        )
      })}
      {dims.map((d, i) => {
        const [x, y] = pt(i, 1.17)
        const anchor =
          Math.abs(x - cx) < 14 ? 'middle' : x > cx ? 'start' : 'end'
        return (
          <text
            key={i}
            x={x}
            y={y}
            fontSize="11"
            fontWeight="600"
            fill="#0E1020"
            textAnchor={anchor as any}
            dominantBaseline="middle"
          >
            {d.label.split(' & ')[0]}
          </text>
        )
      })}
      {dims.map((d, i) => {
        const [x, y] = pt(i, d.score / 100)
        return (
          <text
            key={'s' + i}
            x={x}
            y={y - 9}
            fontSize="11"
            fontWeight="700"
            fill="#0E1020"
            textAnchor="middle"
          >
            {d.score}
          </text>
        )
      })}
    </svg>
  )
}
