import React, { useState, useEffect } from 'react'
import Chart from 'react-google-charts'

const MovieChart = props => {

  const [voteRows, setVoteRows] = useState([[0,0, "", "color: #fff" ]])
  const [ratingRows, setRatingRows] = useState([[0,0, "", "color: #fff" ]])
  const [title, setTitle] = useState("")
  const [episodeCount, setEpisodeCount] = useState(200)

  const parseJson = data => {
    setTitle(data["title"])
    setVoteRows(data["numVotes"])
    setRatingRows(data["averageRating"])
    const n = data["numVotes"].length - 1
    setEpisodeCount(data["numVotes"][n][0])
  }

  useEffect(() => {
    const url = `http://localhost:5000/episodes/${props.tconst}`
    fetch(url).then(
      res => res.json()
    ).then(
      data => {
        parseJson(data)
      }
    )
  }, [props.tconst])

  
  const optionsTemplate = {
    tooltip: { isHtml: true, trigger: 'both' },
      pointSize: 4,
      legend: 'none',
      hAxis: { 
        title: "Episode Number" ,
        format: 0,
        viewWindow: {min: 1, max: episodeCount}},
      lineWidth: (props.line === true) ? 3 : 0,
      // trendlines: { 0: {} },
      // explorer: {axis: 'horizontal', keepInBounds: true, maxZoomOut: 1}
    }

  const ratingOptions = {
    ...optionsTemplate,
    title:  `IMDB Average Rating - ${title}`,
    vAxis: { 
      title: "Average Rating",
      viewWindow: (props.scaleY) ? {min: 0, max: 10} : {},
      scaleType: (props.logScale) ? "log" : "linear"
    },
    width_units: '%'
  }

  const votesOptions = {
    ...optionsTemplate,
    title: `IMDB Votes - ${title}`,
    vAxis: { title: "Number of Votes", scaleType: (props.logScale) ? "log" : "linear" },
  }

  return (
    <>
    {
      (props.type === "rating") ?
        <Chart
          chartType='ScatterChart'
          data={[[
            "Episode",
            "Rating",
            { role: "tooltip", type: "string", p: { html: true }},
            { role: (props.showColors ? "style" : "none" )}
          ], ...ratingRows]}
          width="100%"
          height="600px"
          loader={<div>Loading Chart...</div>}
          options={ratingOptions}
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
          options={votesOptions}
        />
    }
    </>
  )
}

export default MovieChart