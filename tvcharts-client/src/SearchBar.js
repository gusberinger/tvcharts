import React, {useState} from 'react'
import './SearchBar.css'
import Fuse from 'fuse.js'

const SearchBar = ({placeholder, data, selectItem}) => {
  const [filteredData, setFilteredData] = useState([])
  const [searchTerm, setSearchTerm] = useState("")
  const fuse = new Fuse(data, {includeScore: true, keys: ["title"]})

  const handleChange = (e) => {
    const newSearchTerm = e.target.value
    if (searchTerm !== "") {
      const results = fuse.search(newSearchTerm)
      const newFilter = results.filter(item => item.score < .3)
      setFilteredData(newFilter)
    }
    else {
      setFilteredData([])
    }
    setSearchTerm(newSearchTerm)
  }


  const handleSelect = e => {
    e.preventDefault()
    setFilteredData([])
    setSearchTerm("")
    selectItem(e)
  }

  return (
    <div className='search'>
      <div className="searchInputs">
        <input
          type="text"
          placeholder={placeholder}
          onChange={handleChange}
          value={searchTerm}
        />
      </div>
      <div className="dataResult">
        {filteredData.slice(0, 8).map((value, index) => {
          // console.log(value, index)
          return (
          <a
            className="dataItem"
            target="_blank"
            onClick={handleSelect}
            // id={value.id}
            key={index}
            href="# "
          >
            <p tconst={value.item.tconst} title={value.item.title}>{value.item.title} ({value.item.startYear}–{value.item.endYear})</p>
          </a>
          )
        })}
      </div>
    </div>
  )
}

export default SearchBar