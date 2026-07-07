import React from "react";
import styles from "./SponsScroll.module.css";

const sponsorsScroll = () => {
  const sponsors = [
    "/spons-image/safar.png",
    "/spons-image/AUOS.png",
    "/spons-image/BD.png",
    "/spons-image/Bluestar.png",
    "/spons-image/CanaraBank.png",
    "/spons-image/Cisco.png",
    "/spons-image/CocaCola.png",
    "/spons-image/CrownePlaza.png",
    "/spons-image/CushmanWakefield.png",
    "/spons-image/MTv.png",
    "/spons-image/Netmagic.png",
    "/spons-image/NewsVoir.png",
    "/spons-image/Ohcampus.png",
    "/spons-image/RedBull.png",
    "/spons-image/RedFM.png",
    "/spons-image/Saavn.png",
    "/spons-image/SBI.png",
    "/spons-image/Scientech.png",
  ];

  const sponsors2 = [
    "/spons-image/Daikin.png",
    "/spons-image/Dasmesh.png",
    "/spons-image/Ebay.png",
    "/spons-image/FisherScientific.png",
    "/spons-image/Fortinet.png",
    "/spons-image/Fuccha.png",
    "/spons-image/Gail.png",
    "/spons-image/HCL.png",
    "/spons-image/Heico.png",
    "/spons-image/HHV.png",
    "/spons-image/OneIndia.png",
    "/spons-image/Onoma.png",
    "/spons-image/PayU.png",
    "/spons-image/Pepsi.png",
    "/spons-image/Shopclues.png",
    "/spons-image/Sparx.png",
    "/spons-image/Spykar.png",
    "/spons-image/Supersonic.png",
    "/spons-image/TSeries.png",
  ];

  const sponsors3 = [
    "/spons-image/IndraprasthaGasLtd.png",
    "/spons-image/InduslandBank.png",
    "/spons-image/inUth.png",
    "/spons-image/Jio.png",
    "/spons-image/JuniperNetworks.png",
    "/spons-image/KewauneeScientificCorp.png",
    "/spons-image/L&T.png",
    "/spons-image/LiveIndiaTours.png",
    "/spons-image/MDH.png",
    "/spons-image/Playstation.png",
    "/spons-image/ProactiveDataSystems.png",
    "/spons-image/Radisson.png",
    "/spons-image/RaniFloat.png",
    "/spons-image/Tetronics.png",
    "/spons-image/TOINewspaper.png",
    "/spons-image/Unitop.png",
    "/spons-image/Wildcraft.png",
    "/spons-image/WWF.png",
  ];

  return (
    <div>
      {/* Row 1 */}
      <div className={styles.scrollContainer}>
        <div className={styles.scroll}>
          {[...Array(4)].map((_, setIndex) => (
            <div key={`set1-${setIndex}`} className={styles.scrollContent}>
              {sponsors.map((sponsor, index) => (
                <img
                  key={`sponsor-${setIndex}-${index}`}
                  src={sponsor}
                  alt={`Sponsor ${index + 1}`}
                  className="h-16 w-auto object-contain flex-shrink-0"
                />
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* Row 2 */}
      <div className={styles.scrollContainer}>
        <div className={styles.scroll}>
          {[...Array(4)].map((_, setIndex) => (
            <div key={`set2-${setIndex}`} className={styles.scrollContent}>
              {sponsors2.map((sponsor, index) => (
                <img
                  key={`sponsor2-${setIndex}-${index}`}
                  src={sponsor}
                  alt={`Sponsor ${index + 1}`}
                  className="h-16 w-auto object-contain flex-shrink-0"
                />
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* Row 3 (Kingfisher row with extra margin below) */}
      <div className={`${styles.scrollContainer} ${styles.Row3}`}>
        <div className={styles.scroll}>
          {[...Array(4)].map((_, setIndex) => (
            <div key={`set3-${setIndex}`} className={styles.scrollContent}>
              {sponsors3.map((sponsor, index) => (
                <img
                  key={`sponsor3-${setIndex}-${index}`}
                  src={sponsor}
                  alt={`Sponsor ${index + 1}`}
                  className="h-16 w-auto object-contain flex-shrink-0"
                />
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default sponsorsScroll;
