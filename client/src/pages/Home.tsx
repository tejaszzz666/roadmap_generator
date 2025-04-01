import React from 'react'

export default function Home() {
    return (
        <div className='block bg-black text-white w-144 h-screen top-16 left-2'>
            <div className='block ' style={{ width: 500, margin: 'auto', justifyContent: 'center', paddingTop: 150 }}>
                <h1 className=' font-bold pt-0' style={{ fontSize: 33, width: 700, margin: 'auto' }} >Reconnect:Your AI-Powered Career Guide</h1>

                <p className=' p-20 pt-10 ' style={{ width: 600, alignContent: 'center', fontSize: 20 }}>Navigate Your Path with Personalized Guidance and Roadmaps in the Era of Automation and AI</p>

                <button className="text-white bg-orange-700 hover:bg-orange-800 focus:ring-4 focus:ring-orange-300 font-medium rounded-lg text-sm px-4 lg:px-5 py-2 lg:py-2.5 mr-2 focus:outline-none"

                    style={{ borderRadius: 20, background: 'linear-gradient(90deg, #090979 100%, #5941AF 100% )', width: 120, height: 50, marginLeft: 200, }}>TRY NOW</button>
            </div>

            <div className='block  bg-black text-white w-96 h-screen top-16 left-2' style={{ width: 500, margin: 'auto', justifyContent: 'center', paddingTop: 150, paddingBottom:100}}>
                <h1 style={{ fontSize: 40, width: 700, margin: 'auto', paddingTop: 50, paddingLeft: 85 }} >ROADMAP GENERATOR</h1>
                <div style={{ display: 'flex', marginBottom: 10 }}>
                    <input
                        type="text"
                        className='ouline-none w-full py-1 px-3'
                        placeholder='Type Career Path e.g, Data Scientist'
                        readOnly
                        style={{ width: 360, borderRadius: 8, overflow: 'hidden', border: 'white', padding: 10, paddingLeft: 15, marginLeft: 25, fontSize: 16 }}
                    />
                    <button
                        style={{ outline: 'none', backgroundColor: 'darkblue', color: 'white', flexShrink: 0, padding: 10, paddingLeft: 15, fontSize:23 }}
                    >Generate</button>
                </div>

            </div>


        </div>
    );
}

