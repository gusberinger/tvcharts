import React, {useState} from 'react'
import './SearchBar.css'


const SearchBar = ({placeholder, data, selectItem, key}) => {
  const [filteredData, setFilteredData] = useState([])
  const [word, setWord] = useState("")

  const handleChange = (e) => {
    const searched = e.target.value
    setWord(searched)
    if (word != "") {
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
        {filteredData.slice(0, 4).map((value, key) => {
          return (
          <a className="dataItem" target="_blank" onClick={handleSelect} id={value.id}>
            <p tconst={value.id}>{value.title} ({value.startYear}–{value.endYear})</p>
          </a>
          )
        })}
      </div>
    </div>
  )
}

export default SearchBar