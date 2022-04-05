import React, { useState, useEffect } from 'react'
import Chart from 'react-google-charts'

const MovieChart = props => {

  const [voteRows, setVoteRows] = useState([])
  const [ratingRows, setRatingRows] = useState([])
  const [title, setTitle] = useState("")
  const colors = ["#8dd3c7", "#bebada", "#fb8072", "#80b1d3", "#fdb462", "#b3de69", "#fccde5", "#d9d9d9"]

  const parseJson = data => {
    let ratingRows = []
    let voteRows = []
    let episodeIndex = 0
    for (const seasonNumber of Object.keys(data)) {
      if (seasonNumber == -1) {
        setTitle(data[seasonNumber])
      }
      else {
        const seasonColor = `color: ${colors[(seasonNumber -1 ) % colors.length]}`
        for (const episodeNumber of Object.keys(data[seasonNumber])) {
          const episode = data[seasonNumber][episodeNumber]
          episodeIndex++
          const title = episode['title']
          const rating = episode['rating']
          const votes = episode['votes']
          const annotation = `<b>Season ${seasonNumber} Epsiode ${episodeNumber}</b><br/>${title}<br/>${votes.toLocaleString('en-US')} Votes<br/>${rating} Average Rating`
          ratingRows.push([episodeIndex, rating, annotation, seasonColor])
          voteRows.push([episodeIndex, votes, annotation, seasonColor])
        }
      }
    }
    setRatingRows(ratingRows)
    setVoteRows(voteRows)
  }

  useEffect(() => {
    fetch(`/tconst/${props.tconst}`).then(
      res => res.json()
    ).then(
      data => {
        parseJson(data)
      }
    )
  }, [])

  return (
    <>
    {
      (props.type == "rating") ?
        <Chart
          chartType='ScatterChart'
          data={[[
            "Episode",
            "Rating",
            { role: "tooltip", type: "string", p: { html: true }},
            { role: "style"}
          ], ...ratingRows]}
          width="100%"
          height="600px"
          loader={<div>Loading Chart...</div>}
          options={{
            title:  `IMDB Average Rating - ${title}`,
            tooltip: { isHtml: true },
            pointSize: 4,
            legend: 'none',
            vAxis: { title: "Average Rating" },
            hAxis: { title: "Episode Number" },
            lineWidth: (props.line == true) ? 3 : 0
          }}
          // chartWrapperParams={{ view: { columns: [0,2,3,4]} }}
        /> :
        <Chart
          chartType='ScatterChart'
          data={[[
            "Episode",
            "Votes",
            { role: "tooltip", type: "string", p: { html: true }},
            { role: "style"}
          ], ...voteRows]}
          width="100%"
          height="600px"
          loader={<div>Loading Chart...</div>}
          options={{
            title: `IMDB Votes - ${title}`,
            tooltip: { isHtml: true },
            pointSize: 4,
            legend: 'none',
            vAxis: { title: "Number of Votes" },
            hAxis: { title: "Episode Number" },
            lineWidth: (props.line == true) ? 3 : 0
          }}
          // chartWrapperParams={{ view: { columns: [0,2,3,4]} }}
        />
    }
    </>
  )
}

export default MovieChart