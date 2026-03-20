import React from 'react'
import TopNavigation from './TopNavigation'
import { useSelector } from 'react-redux'

function Dashboard() {
    let userDetails = useSelector((store)=>{
    return store.userDetails
    });
    console.log(userDetails);

    let onDeleteProfile = async ()=>{
      let dataToSend = new FormData()
      dataToSend.append("email",userDetails.email)

      let reqOptions ={
        method:"DELETE",
        body:dataToSend
      }

      let JSONData = await fetch("http://localhost:8000/deleteProfile",reqOptions);

        let JSOData = await JSONData.json();
        console.log(JSOData)
        alert(JSOData.msg)
    }
  return (
    <div>

        <TopNavigation></TopNavigation>
      <h2>Dashboard</h2>
      <button type='button' onClick={()=>{
        onDeleteProfile()
      }}>Delete Account</button>
      <h1>{userDetails.firstName} {userDetails.lastName}</h1>
      <h3>{userDetails.age}</h3>
      <h3>{userDetails.mobileNo}</h3>
      <img src={`http://localhost:8000/${userDetails.profilePic}`} alt=''></img>
    </div>
  )
}

export default Dashboard
