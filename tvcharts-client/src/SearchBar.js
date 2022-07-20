import React, {useState} from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import './SearchBar.css'


const SearchBar = ({placeholder, data, selectItem}) => {
  const [filteredData, setFilteredData] = useState([])
  const [word, setWord] = useState("")

  const handleChange = (e) => {
    const word = e.target.value
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
        />
        <div className="searchIcon">
          <i className="fa-pencil" title="Edit"></i>
          {/* <FontAwesomeIcon icon="fa-solid fa-magnifying-glass" /> */}
          {/* {filteredData.length != 0 ? <FontAwesomeIcon icon="fa-solid fa-magnifying-glass" /> : <FontAwesomeIcon icon="fa-solid fa-x" />} */}
        </div>
      </div>
      <div className="dataResult">
        {filteredData.slice(0, 4).map((value, key) => {
          return (
          <a className="dataItem" target="_blank" onClick={handleSelect} id={value.id}>
            <p tconst={value.id}>{value.title}</p>
          </a>
          )
        })}
      </div>
    </div>
  )
}

export default SearchBar