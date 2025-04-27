import { Component, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import Header from './components/header'
import Advertising from './components/advertising'

function App() {
 const count = 1


  return (
    <>
      <div>
      
        <Header/>
        <Advertising/>

      </div>
    </>
  )
}

export default App
