import React, {useState} from 'react'
import MovieChart from './MovieChart'

const MovieForm = () => {
  const [type, setType] = useState("rating")
  const [lines, setLines] = useState(true)
  const [searchText, setSearchText] = useState("")


  const setMovie = (data) => {
    console.log(searchText)
  }

  const handleSearch = e => {
    const val = e.target.value
    setSearchText(val)
    if (val.length > 4) {
      // get searches
    }

  }

  return (
    <>
      <section>
        <button onClick={() => setLines(!lines)}>{lines ? "Hide Lines" : "Show Lines"}</button>
        <button onClick={() => (type == "rating") ? setType("votes") : setType("rating")}>{(type == "rating") ? 'Rating' : 'Votes'}</button>
        <input type="text" value={searchText} onChange={e => setSearchText(e.target.value)}/>
        <button onClick={setMovie}>Search Movie</button>
      </section>
      <div><MovieChart tconst="tt1439629" type={type} line={lines}/></div>
    </>
  )
}

export default MovieForm