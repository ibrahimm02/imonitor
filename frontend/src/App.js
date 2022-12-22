import './App.css';
import React, {useState, useEffect, children} from 'react'

import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';

// function App() {

//   const [data, setData] = useState([{}])

//   useEffect(() => {
//     fetch("/members").then(
//       res => res.json()
//     ).then(
//       data => {
//         setData(data)
//         console.log(data)
//       }
//     )
//   }, [])

//   return (
//     <div>

      // {(typeof data.members === 'undefined') ? (
      //   <p>Loading...</p>
      // ) : (
      //   data.members.map((member, i) => (
      //     <p key={i}>{member}</p>
      //   ))
      // )}


//     </div>
//   )
// }


function App() {

  const [isOpened, setIsOpened] = useState(false);

  useEffect(() => {
    fetch("/members").then(
      res => res.json()
    ).then(
      data => {
        setIsOpened(data)
        console.log(data)
      }
    )
  }, [])

  return (
    <div className="App">
      <div className="header">
        <div className="icon" onClick={() => setIsOpened(!isOpened)}>
          {isOpened ? <ChevronLeftIcon /> : <MenuIcon />}
        </div>
        <div className="header-title">Header</div>
      </div>
      <div className="container">
        <aside className={`${isOpened ? "opened" : ""} drawer`}>Drawer</aside>
        <main className="main">{children}</main>
      </div>
      <div className="footer">Footer</div>
    </div>
  );
}

const Members = () => {

  const [data, setData] = useState([{}])

  useEffect(() => {
    fetch("/members").then(
      res => res.json()
    ).then(
      data => {
        setData(data)
        console.log(data)
      }
    )
  }, [])

  return (
    <div>

      {(typeof data.members === 'undefined') ? (
        <p>Loading...</p>
      ) : (
        data.members.map((member, i) => (
          <p key={i}>{member}</p>
        ))
      )}


    </div>
  )
}

export default {App, Members}

