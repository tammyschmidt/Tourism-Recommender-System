import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Star, MapPin, Phone, ExternalLink, Loader2, AlertCircle, Utensils } from "lucide-react"
import { 
  type Restaurant,
  getPopularRestaurants,
  getLocationRecommendations,
  getCityRecommendations,
  getUserRecommendations,
  geocodeLocation
} from "@/services/api"

interface SearchCriteria {
  location: string
  cuisines: string[]
  setting: string
  preferences: {
    price: number[]
    distance: number[]
    rating: number[]
    waitTime: number[]
  }
  selectedUser: string
}

interface RestaurantResultsProps {
  searchCriteria: SearchCriteria
}



export default function RestaurantResults({ searchCriteria }: RestaurantResultsProps) {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const getPriceSymbol = (level: number) => {
    return (
      "€".repeat(level) +
      "€"
        .repeat(Math.max(0, 3 - level))
        .split("")
        .map((char, i) =>
          i < level ? (
            char
          ) : (
            <span key={i} className="opacity-30">
              {char}
            </span>
          ),
        )
    )
  }

  const fetchRestaurants = async () => {
    setLoading(true)
    setError(null)
    
    try {
      let results: Restaurant[] = []
      
      // Convert preferences to weights
      const weights = {
        price: searchCriteria.preferences.price[0] / 100,
        distance: searchCriteria.preferences.distance[0] / 100,
        rating: searchCriteria.preferences.rating[0] / 100,
      }
      
      if (searchCriteria.selectedUser) {
        // User-based recommendations
        const request = {
          city: searchCriteria.location || 'Berlin',
          categories: searchCriteria.cuisines.length > 0 ? searchCriteria.cuisines : undefined,
          attributes: searchCriteria.setting ? [searchCriteria.setting] : undefined,
        }
        results = await getUserRecommendations(searchCriteria.selectedUser, request)
      } else if (searchCriteria.location) {
        // Check if location looks like a city name or coordinates
        const isCity = isNaN(parseFloat(searchCriteria.location))
        
        if (isCity) {
          // City-based recommendations
          const request = {
            city: searchCriteria.location,
            categories: searchCriteria.cuisines.length > 0 ? searchCriteria.cuisines : undefined,
            attributes: searchCriteria.setting ? [searchCriteria.setting] : undefined,
            weights: Object.keys(weights).length > 0 ? weights : undefined,
          }
          results = await getCityRecommendations(request)
        } else {
          // Try to geocode the location for location-based search
          try {
            const coordinates = await geocodeLocation(searchCriteria.location)
            const request = {
              latitude: coordinates.latitude,
              longitude: coordinates.longitude,
              max_distance: 5000, // 5km default
              categories: searchCriteria.cuisines.length > 0 ? searchCriteria.cuisines : undefined,
              attributes: searchCriteria.setting ? [searchCriteria.setting] : undefined,
              weights: Object.keys(weights).length > 0 ? weights : undefined,
            }
            results = await getLocationRecommendations(request)
          } catch (geocodeError) {
            // Fallback to city search if geocoding fails
            const request = {
              city: searchCriteria.location,
              categories: searchCriteria.cuisines.length > 0 ? searchCriteria.cuisines : undefined,
              attributes: searchCriteria.setting ? [searchCriteria.setting] : undefined,
              weights: Object.keys(weights).length > 0 ? weights : undefined,
            }
            results = await getCityRecommendations(request)
          }
        }
      } else {
        // Default to popular restaurants
        results = await getPopularRestaurants()
      }
      
      setRestaurants(results)
    } catch (err) {
      console.error('Error fetching restaurants:', err)
      setError(err instanceof Error ? err.message : 'An error occurred while fetching restaurants')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRestaurants()
  }, [searchCriteria])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin mr-2" />
        <span className="text-lg">Finding restaurants...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-4" />
          <p className="text-red-600 mb-4">{error}</p>
          <Button 
            variant="outline" 
            onClick={fetchRestaurants}
          >
            Try Again
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">Restaurants Found</h2>
        <p className="text-gray-600">
          {restaurants.length} restaurants found
          {searchCriteria.location && ` in ${searchCriteria.location}`}
          {searchCriteria.selectedUser && ` for ${searchCriteria.selectedUser}`}
        </p>
      </div>

      {restaurants.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg mb-4">No restaurants found matching your criteria.</p>
          <Button onClick={fetchRestaurants} variant="outline">
            Search Again
          </Button>
        </div>
      ) : (
        <div className="grid gap-6">
          {restaurants.map((restaurant) => (
          <Card key={restaurant.id} className="overflow-hidden hover:shadow-lg transition-shadow">
            <div className="md:flex">
              <div className="md:w-1/3">
                <div className="w-full h-48 md:h-full bg-gradient-to-br from-orange-100 to-red-100 flex items-center justify-center">
                  <Utensils className="w-16 h-16 text-orange-400" />
                </div>
              </div>
              <div className="md:w-2/3">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-xl">{restaurant.name}</CardTitle>
                      <CardDescription className="flex items-center gap-4 mt-1">
                        {restaurant.categories && restaurant.categories.length > 0 && (
                          <Badge variant="outline">{restaurant.categories[0]}</Badge>
                        )}
                        <div className="flex items-center gap-1">
                          <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                          <span className="font-medium">{restaurant.rating}</span>
                        </div>
                        <div className="flex items-center">{getPriceSymbol(restaurant.price_level)}</div>
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {restaurant.description && (
                    <p className="text-gray-600 mb-4">{restaurant.description}</p>
                  )}

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                    <div className="flex items-center gap-2 text-sm">
                      <MapPin className="w-4 h-4 text-gray-400" />
                      <span>{restaurant.address}</span>
                    </div>
                    {restaurant.phone && (
                      <div className="flex items-center gap-2 text-sm">
                        <Phone className="w-4 h-4 text-gray-400" />
                        <span>{restaurant.phone}</span>
                      </div>
                    )}
                  </div>

                  {restaurant.categories && restaurant.categories.length > 1 && (
                    <div className="flex flex-wrap gap-2 mb-4">
                      {restaurant.categories.slice(1).map((category, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {category}
                        </Badge>
                      ))}
                    </div>
                  )}

                  <div className="flex gap-2">
                    {restaurant.phone && (
                      <Button className="flex-1" onClick={() => window.open(`tel:${restaurant.phone}`)}>
                        <Phone className="w-4 h-4 mr-2" />
                        Call
                      </Button>
                    )}
                    <Button 
                      variant="outline" 
                      className="flex-1"
                      onClick={() => window.open(`https://maps.google.com/?q=${encodeURIComponent(restaurant.address)}`, '_blank')}
                    >
                      <ExternalLink className="w-4 h-4 mr-2" />
                      View on Map
                    </Button>
                  </div>
                </CardContent>
              </div>
            </div>
          </Card>
          ))}
        </div>
      )}
    </div>
  )
}