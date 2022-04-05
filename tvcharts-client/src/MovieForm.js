import React, {useState} from 'react'
import MovieChart from './MovieChart'

const MovieForm = () => {
  const [type, setType] = useState("rating")
  const [lines, setLines] = useState(true)
  return (
    <>
      <section>
        <button onClick={() => setLines(!lines)}>{lines ? "Hide Lines" : "Show Lines"}</button>
        <button onClick={() => (type == "rating") ? setType("votes") : setType("rating")}>{(type == "rating") ? 'Rating' : 'Votes'}</button>
      </section>
      <div><MovieChart tconst="tt1439629" type={type} line={lines}/></div>
    </>
  )
}

export default MovieForm