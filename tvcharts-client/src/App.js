import React, {useState, useEffect} from 'react'
import MovieChart from './MovieChart'
import SearchBar from './SearchBar'
import './App.css'


const topShows = [
  "tt2297757",
  "tt0141842",
  "tt0903747",
  "tt0386676",
  "tt0098904",
  "tt0108778",
]


const App = () => {
  const [type, setType] = useState("rating")
  const [lines, setLines] = useState(true)
  const [scaleY, setScaleY] = useState(false)
  const [colors, setColors] = useState(true)
  const [show, setShow] = useState(topShows[Math.floor(Math.random()*topShows.length)])
  const [searchData, setSearchData] = useState([{}])

  useEffect(() => {
    fetch(`/search/`).then(
      res => res.json()
    ).then(
      data => {
        setSearchData(data)
      }
    )
  }, [])


  const selectItem = e => {
    const newShow = e.target.getAttribute("tconst")
    console.log(newShow)
    setShow(newShow)
  }

  return (
    <>
      <section>
      <h1 className='site-title center-text'>TV Charts</h1>
      <div className='hero'>

        <img src={`/poster/${show}`} alt=""/>
        <div className="selectMovie">
          <button onClick={() => setLines(!lines)}>{lines ? "Hide Lines" : "Show Lines"}</button>
          <button onClick={() => (type == "rating") ? setType("votes") : setType("rating")}>{(type == "rating") ? 'Rating' : 'Votes'}</button>
          {(type == "rating") ? 
          <button onClick={() => setScaleY(!scaleY)}>{scaleY ? "Scale Y-Axis" : "Unscale Y-Axis"}</button>
          : <></>}
          <button onClick={() => setColors(!colors)}>{colors ? "Hide Colors" : "Show Colors"}</button>
        </div>
        <SearchBar placeholder="Search TV Show" data={searchData} selectItem={selectItem}/>
      </div>
      </section>
      <div><MovieChart
        tconst={show}
        type={type}
        line={lines}
        scaleY={scaleY}
        showColors = {colors}
      />
      </div>
    </>
  )
}

export default App