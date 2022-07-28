import React, {useState, useEffect} from 'react'
import MovieChart from './MovieChart'
import SearchBar from './SearchBar'
import './App.css'
import SeasonChart from './SeasonChart'


const topShows = [
  "tt0141842",
  "tt0903747",
  "tt0386676",
  "tt0098904",
  "tt0108778",
]
const topShowsTitles = [
  "The Sopranos",
  "Breaking Bad",
  "The Office",
  "Seinfeld",
  "Friends"
]


const App = () => {
  const [type, setType] = useState("rating")
  const [lines, setLines] = useState(true)
  const [scaleY, setScaleY] = useState(true)
  const [colors, setColors] = useState(true)
  const [logScale, setLogScale] = useState(false)
  const n = Math.floor(Math.random()*topShows.length)
  const [show, setShow] = useState(topShows[n])
  const [title, setTitle] = useState(topShowsTitles[n])
  const [searchData, setSearchData] = useState([{}])

  useEffect(() => {
    const url = `http://localhost:5000/search`
    fetch(url).then(
      res => res.json()
    ).then(
      data => {
        setSearchData(data)
      }
    )
  }, [])


  const selectItem = e => {
    const newShow = e.target.getAttribute("tconst")
    const newTitle = e.target.getAttribute("title")
    console.log(e.target)
    console.log(newTitle)
    setShow(newShow)
    setTitle(newTitle)
  }

  return (
    <>
      <section>
        <h1 className='site-title center-text'>TV Charts</h1>
        <h2 className='site-subtitle center-text'>{title}</h2>
        <div className="split">
          <img src={`http://localhost:5000/poster/${show}`} alt=""/>
          <div className="chartOptions">
            <button onClick={() => setLines(!lines)}>{lines ? "Hide Lines" : "Show Lines"}</button>
            <button onClick={() => (type === "rating") ? setType("votes") : setType("rating")}>{(type === "rating") ? 'Rating' : 'Votes'}</button>
            {(type === "rating") ? 
            <button onClick={() => setScaleY(!scaleY)}>{scaleY ? "Complete Y-Axis" : "Limit Y-Axis"}</button>
            : <></>}
            <button onClick={() => setColors(!colors)}>{colors ? "Hide Colors" : "Show Colors"}</button>
            <button onClick={() => setLogScale(!logScale)}>{logScale ? "Log Scale" : "Linear Scale"}</button>
          </div>
        </div>
      </section>
      <section>
        <div className="search-bar">
          <SearchBar placeholder="Search TV Show" data={searchData} selectItem={selectItem}/>
        </div>
      {/* </section> */}
      {/* <section> */}
        <div>
          <MovieChart
            tconst={show}
            type={type}
            line={lines}
            scaleY={scaleY}
            logScale={logScale}
            showColors = {colors}
          />
          <SeasonChart
            tconst={show}
            type={type}
            title={title}
            scaleY={scaleY}
            logScale={logScale}
            line={lines}
          />
        </div>
      </section>
    </>
  )
}

export default App