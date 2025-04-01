import React from 'react'

export default function Header() {
    return (
        <header className='sticky top-0 '>
            <nav className='bg-black px-4 lg:px-6 py-2.5'>
                <div className="flex flex-wrap justify-between items-center mx-auto max-w-screen-xl">

                    <h1 className='flex text-white font-bold text-3xl'>RECONNECT</h1>

                    <div className="flex items-center lg:order-2">
                        <button className="text-white bg-orange-700 hover:bg-orange-800 focus:ring-4 focus:ring-orange-300 font-medium rounded-lg text-sm px-4 lg:px-5 py-2 lg:py-2.5 mr-2 focus:outline-none"

                            style={{ borderRadius: 20, background: 'linear-gradient(90deg, #090979 100%, #5941AF 100% )', width: 120, height: 50 }}>JOIN NOW</button>

                    </div>
                </div>
            </nav>

        </header>
    );
}

