import React, { useState, useEffect } from 'react'
import Chart from 'react-google-charts'

const App = () => {

  const [rows, setRows] = useState([])

  const colors = ["#1A181B", "#564D65", "#3E8989", "#2CDA9D", "#05F140"]

  const parseJson = data => {
    let rows = []
    let episodeIndex = 0
    for (const seasonNumber of Object.keys(data)) {
      const seasonColor = `color: ${colors[seasonNumber % colors.length]}`
      for (const episodeNumber of Object.keys(data[seasonNumber])) {
        const episode = data[seasonNumber][episodeNumber]
        episodeIndex++
        rows.push([episodeIndex, episode['rating'], episode['title'], seasonColor])
      }
    }
    return rows
  }

  useEffect(() => {
    fetch("/tconst/tt1439629").then(
      res => res.json()
    ).then(
      data => {
        let rows = parseJson(data)
        setRows(rows)
        console.log(rows)
      }
    )
  }, [])

  return (
    <Chart
      chartType='ScatterChart'
      data={[[
        "Episode",
        "Rating",
        { role: "tooltip", type: "string", p: { html: true }},
        { role: "style"}
      ], ...rows]}
      width="100%"
      height="600px"
      legendToggle={false}
      loader={<div>Loading Chart</div>}
      options={{
        title: 'IMDB Rating',
        tooltip: { isHtml: true, trigger: "visible" },
        pointSize: 4
      }}
    />
  )
}

export default App