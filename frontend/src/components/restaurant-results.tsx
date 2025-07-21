import { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Star, MapPin, Phone, ExternalLink, Loader2, AlertCircle, Utensils } from "lucide-react"
import { 
  type Restaurant,
  type RecommendationRequest,
  getPopularRestaurants,
  getRecommendations,
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
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const getPriceSymbol = (level: number | null) => {
    if (level === null || level < 1) return null;
    return (
      "€".repeat(level) +
      <span className="opacity-30">{"€".repeat(Math.max(0, 4 - level))}</span>
    )
  }

  const fetchRestaurants = useCallback(async () => {
    setLoading(true)
    setError(null)
    
    try {
      let results: Restaurant[] = []
      
      if (searchCriteria.selectedUser) {
        results = await getUserRecommendations(searchCriteria.selectedUser, {
          city: searchCriteria.location || 'Nashville',
          categories: searchCriteria.cuisines,
          attributes: searchCriteria.setting ? [searchCriteria.setting] : undefined,
        })
      } else if (searchCriteria.location || searchCriteria.cuisines.length > 0 || searchCriteria.setting) {
        const request: RecommendationRequest = { top_n: 20 }

        if (searchCriteria.location) {
          try {
            const coordinates = await geocodeLocation(searchCriteria.location)
            request.latitude = coordinates.latitude
            request.longitude = coordinates.longitude
            request.city = searchCriteria.location
            request.maxDistance = 5000
          } catch (geocodeError) {
            console.warn("Geocoding failed, falling back to city search:", geocodeError)
            request.city = searchCriteria.location
          }
        }
        
        if (searchCriteria.cuisines.length > 0) {
          request.inputCategories = searchCriteria.cuisines
        }

        if (searchCriteria.setting) {
          request.requiredAttributes = [searchCriteria.setting]
        }
        
        const prefs = searchCriteria.preferences;
        request.weights = [
          1.0,
          prefs.price[0] / 100,
          prefs.rating[0] / 100,
          prefs.distance[0] / 100,
        ];

        results = await getRecommendations(request)
      } else {
        results = await getPopularRestaurants()
      }
      
      setRestaurants(results)
    } catch (err) {
      console.error('Error fetching restaurants:', err)
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred.'
      setError(`Failed to fetch restaurants. ${errorMessage}`)
    } finally {
      setLoading(false)
    }
  }, [searchCriteria])

  useEffect(() => {
    fetchRestaurants()
  }, [fetchRestaurants])

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
        <div className="text-center p-4 border border-red-200 bg-red-50 rounded-lg">
          <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-4" />
          <p className="text-red-600 mb-4 font-semibold">Could not load results</p>
          <p className="text-sm text-red-500 mb-4">{error}</p>
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
        <h2 className="text-2xl font-bold mb-2">Your Recommendations</h2>
        <p className="text-muted-foreground">
          {restaurants.length} results found
        </p>
      </div>

      {restaurants.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground text-lg mb-4">No restaurants found matching your criteria.</p>
          <p className="text-sm text-muted-foreground">Try adjusting your filters.</p>
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
              <div className="md:w-2/3 p-4">
                <CardHeader className="p-2">
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-xl">{restaurant.name || "Unnamed Restaurant"}</CardTitle>
                      <CardDescription className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1">
                        {restaurant.categories && restaurant.categories.length > 0 && (
                          <Badge variant="outline">{restaurant.categories[0]}</Badge>
                        )}
                        {restaurant.rating !== null && (
                          <div className="flex items-center gap-1">
                            <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                            <span className="font-medium">{restaurant.rating.toFixed(1)}</span>
                          </div>
                        )}
                        {restaurant.price_level !== null && (
                           <div className="flex items-center font-semibold text-muted-foreground">{getPriceSymbol(restaurant.price_level)}</div>
                        )}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="p-2">
                  {restaurant.description && (
                    <p className="text-muted-foreground mb-4 text-sm">{restaurant.description}</p>
                  )}

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                    {restaurant.address && (
                      <div className="flex items-start gap-2 text-sm">
                        <MapPin className="w-4 h-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                        <span>{restaurant.address}</span>
                      </div>
                    )}
                    {restaurant.phone && (
                      <div className="flex items-center gap-2 text-sm">
                        <Phone className="w-4 h-4 text-muted-foreground" />
                        <span>{restaurant.phone}</span>
                      </div>
                    )}
                  </div>

                  {restaurant.attributes && restaurant.attributes.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-4">
                      {restaurant.attributes.slice(0, 5).map((attr, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {attr}
                        </Badge>
                      ))}
                    </div>
                  )}

                  <div className="flex gap-2 mt-4">
                    {restaurant.phone && (
                      <Button className="flex-1" size="sm" onClick={() => window.open(`tel:${restaurant.phone}`)}>
                        <Phone className="w-4 h-4 mr-2" />
                        Call
                      </Button>
                    )}
                    {restaurant.address && (
                       <Button 
                        variant="outline" 
                        size="sm"
                        className="flex-1"
                        onClick={() => window.open(`https://maps.google.com/?q=${encodeURIComponent(restaurant.address || '')}`, '_blank')}
                      >
                        <ExternalLink className="w-4 h-4 mr-2" />
                        Map
                      </Button>
                    )}
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