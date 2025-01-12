import { useState } from "react";
import axios from "axios";

const ScrapeDetails = () => {
  const [business, setBusiness] = useState("");
  const [details, setDetails] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    axios
      .post("http://127.0.0.1:8000/crawl/", {
        business_name: business,
      })
      .then((response) => {
        console.log(response.data);
        setDetails(response.data);
      })
      .catch((error) => {
        console.error(error);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <div className="flex justify-center mt-10">
      <div className="grid grid-cols-3 gap-4">
        <div className="col-start-2 flex items-center justify-center">
          <div className="text-center max-w-lg">
            <h1 className="text-4xl font-bold text-accent">
              Business-Scrape Bot!!
            </h1>
            <form
              onSubmit={handleSubmit}
              className="flex justify-center items-center w-full mt-10"
            >
              <input
                type="text"
                placeholder="Enter Business Name"
                className="input input-bordered input-warning w-full max-w-md"
                required
                value={business}
                onChange={(e) => setBusiness(e.target.value)}
              />
              <button className="btn btn-active btn-primary text-black ml-2">
                Search
              </button>
            </form>
            <div className="flex flex-col items-center mt-10">
              {loading ? (
                <span className="loading loading-ring w-14 h-14"></span>
              ) : details.length > 0 ? (
                <table className="table-auto border-collapse border border-gray-400 mt-5">
                  <thead>
                    <tr>
                      <th className="border border-gray-300 px-4 py-2">
                        Corporate Name
                      </th>
                      <th className="border border-gray-300 px-4 py-2">
                        Document Number
                      </th>
                      <th className="border border-gray-300 px-4 py-2">
                        FEIN Number
                      </th>
                      <th className="border border-gray-300 px-4 py-2">
                        Date Filed
                      </th>
                      <th className="border border-gray-300 px-4 py-2">
                        State
                      </th>
                      <th className="border border-gray-300 px-4 py-2">
                        Status
                      </th>
                      <th className="border border-gray-300 px-4 py-2">
                        Principal Address
                      </th>
                      <th className="border border-gray-300 px-4 py-2">
                        Mailing Address
                      </th>
                      <th className="border border-gray-300 px-4 py-2">
                        Registered Agent
                      </th>
                      <th className="border border-gray-300 px-4 py-2">
                        Officer/Director Detail
                      </th>
                      <th className="border border-gray-300 px-4 py-2">
                        Annual Reports
                      </th>
                      <th className="border border-gray-300 px-4 py-2">
                        Document Images
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {details.map((detail, index) => (
                      <tr key={index}>
                        <td className="border border-gray-300 px-4 py-2">
                          {detail.corporate_name}
                        </td>
                        <td className="border border-gray-300 px-4 py-2">
                          {detail.document_number}
                        </td>
                        <td className="border border-gray-300 px-4 py-2">
                          {detail.fein_number}
                        </td>
                        <td className="border border-gray-300 px-4 py-2">
                          {detail.date_filed}
                        </td>
                        <td className="border border-gray-300 px-4 py-2">
                          {detail.state}
                        </td>
                        <td className="border border-gray-300 px-4 py-2">
                          {detail.status}
                        </td>
                        <td
                          className="border border-gray-300 px-4 py-2"
                          dangerouslySetInnerHTML={{
                            __html: detail.principal_address,
                          }}
                        ></td>
                        <td
                          className="border border-gray-300 px-4 py-2"
                          dangerouslySetInnerHTML={{
                            __html: detail.mailing_address,
                          }}
                        ></td>
                        <td
                          className="border border-gray-300 px-4 py-2"
                          dangerouslySetInnerHTML={{
                            __html: detail.registered_agent,
                          }}
                        ></td>
                        <td
                          className="border border-gray-300 px-4 py-2"
                          dangerouslySetInnerHTML={{
                            __html: detail.officer_director_detail,
                          }}
                        ></td>
                        <td className="border border-gray-300 px-4 py-2">
                          {detail.annual_reports.map((link, i) => (
                            <div key={i}>
                              <a
                                href={link}
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                {link}
                              </a>
                            </div>
                          ))}
                        </td>
                        <td className="border border-gray-300 px-4 py-2">
                          {detail.document_images.map((link, i) => (
                            <div key={i}>
                              <a
                                href={link}
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                {link}
                              </a>
                            </div>
                          ))}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p>Please enter a business name and click search</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScrapeDetails;
