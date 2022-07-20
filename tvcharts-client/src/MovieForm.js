import React, {useState, useEffect} from 'react'
import MovieChart from './MovieChart'
import SearchBar from './SearchBar'
import data from './TvData.json'
import './MovieForm.css'
// import { ReactSearchAutocomplete } from 'react-search-autocomplete'


const MovieForm = () => {
  const [type, setType] = useState("rating")
  const [lines, setLines] = useState(true)
  const [show, setShow] = useState("tt0118375")


  const selectItem = e => {
    const newShow = e.target.getAttribute("tconst")
    console.log(newShow)
    setShow(newShow)
  }

  return (
    <>
      <section>
        <div className="selectMovie">
          <button onClick={() => setLines(!lines)}>{lines ? "Hide Lines" : "Show Lines"}</button>
          <button onClick={() => (type == "rating") ? setType("votes") : setType("rating")}>{(type == "rating") ? 'Rating' : 'Votes'}</button>
          <SearchBar placeholder="The Sopranos" data={data} selectItem={selectItem}/>
        </div>
      </section>
      <div><MovieChart tconst={show} type={type} line={lines}/></div>
    </>
  )
}

export default MovieForm