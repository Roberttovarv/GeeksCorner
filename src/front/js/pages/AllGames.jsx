import React, { useContext, useEffect, useState } from "react";
import { Context } from "../store/appContext";
import { Link } from "react-router-dom";
import "../../styles/landing.css";
import { LoadingMario } from "../component/LoadingMario.jsx";

export const AllGames = () => {
    const { store, actions } = useContext(Context);
    const [games, setGames] = useState([]);
    const [search, setSearch] = useState("");
    const [filteredGames, setFilteredGames] = useState([]);

    const host = `${process.env.BACKEND_URL}`;

    const getGames = async () => {
        const uri = host + '/api/games';
        const options = { method: 'GET' };

        const response = await fetch(uri, options);

        if (!response.ok) {
            console.log("Error", response.status, response.statusText);
            return;
        }

        const data = await response.json();
        setGames(data.results);
        setFilteredGames(data.results); 
    };

    const handleInputChange = (event) => {
        setSearch(event.target.value);
    };

    useEffect(() => {
        getGames();
    }, []);

    useEffect(() => {
        const filtered = games.filter(game => 
            game.name.toLowerCase().includes(search.toLowerCase())
        );
        setFilteredGames(filtered);
    }, [search, games]);

    return (
        <div className="container">
            <div className="form__group field float-end ps-5">
                <input 
                    type="input" 
                    className="form__field" 
                    placeholder="Search" 
                    value={search} 
                    onChange={handleInputChange} 
                />
                <label htmlFor="name" className="form__label">Search</label>
            </div>
            <br />
            <br />
            <h1 className="text-center text-light">All Games</h1>
            <h4 className="text-center text-light">Good luck finding your game, freak!</h4>
            {games.length === 0 ? (
                <LoadingMario />
            ) : (
                <div className="row flex-nowrap pb-2 d-flex px-3 m-auto justify-content-center">
                    {filteredGames.map((game, index) => (
                        <div key={index} className="tarjeta m-3 ratio ratio-1x1" style={{ width: '18rem' }}>
                            <img 
                                src={game.background_image} 
                                className="text-light rounded-1" 
                                alt={game.name} 
                                style={{ width: "100%", maxHeight: "60%", objectFit: "cover" }} 
                            />
                            <div className="card-body align-content-end mt-2">
                                <div className="align-content-between mb-2">
                                    <h5 className="card-title text-light rounded-1 d-flex">{game.name}</h5>
                                    <p className="card-text text-light rounded-1">Releasing date: {game.released_at}</p>
                                </div>
                                <div className="d-flex justify-content-between align-items-end">
                                    <Link to={`/game-details/${game.name}`}>
                                        <button className="button" onClick={() => actions.setCurrentItem(game)}>
                                            Details
                                        </button>
                                    </Link>
                                    <span className="text-danger me-2">
                                        <i className="far fa-heart"></i>
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};
