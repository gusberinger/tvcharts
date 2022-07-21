import React, {useState} from 'react'
import './SearchBar.css'


const SearchBar = ({placeholder, data, selectItem}) => {
  const [filteredData, setFilteredData] = useState([])
  const [word, setWord] = useState("")

  const handleChange = (e) => {
    const searched = e.target.value
    setWord(searched)
    if (word !== "") {
      const newFilter = data.filter((value) => {
        return value.title.toLowerCase().includes(word.toLowerCase())
      })
      setFilteredData(newFilter)
    }
    else {
      setFilteredData([])
    }
  }

  const handleSelect = e => {
    e.preventDefault()
    setFilteredData([])
    setWord("")
    selectItem(e)
  }

  return (
    <div className='search'>
      <div className="searchInputs">
        <input
          type="text"
          placeholder={placeholder}
          onChange={handleChange}
          value={word}
        />
      </div>
      <div className="dataResult">
        {filteredData.slice(0, 15).map((value, key) => {
          return (
          <a className="dataItem" target="_blank" onClick={handleSelect} id={value.id} key={key} href="#">
            <p tconst={value.id}>{value.title} ({value.startYear}–{value.endYear})</p>
          </a>
          )
        })}
      </div>
    </div>
  )
}

export default SearchBar